#!/usr/bin/env ruby

require 'google/apis/calendar_v3'
require 'google/apis/people_v1'
require 'googleauth'
require 'googleauth/stores/file_token_store'
require 'fileutils'
require 'json'
require 'webrick'

# Move constants to top level
DATA_DIR = File.join(Dir.home, '.google_data_store')
CREDENTIALS_PATH = File.join(DATA_DIR, 'credentials.json')
TOKEN_PATH = File.join(DATA_DIR, 'token.yaml')

class GoogleDataFetcher
  Calendar = Google::Apis::CalendarV3
  People = Google::Apis::PeopleV1

  APPLICATION_NAME = 'Google Data Fetcher'.freeze
  PORT = 8080
  SCOPES = [
    Google::Apis::CalendarV3::AUTH_CALENDAR_READONLY,
    'https://www.googleapis.com/auth/contacts.readonly'
  ]

  def initialize
    @data_dir = DATA_DIR
    FileUtils.mkdir_p(@data_dir)
    @received_code = nil
  end

  def fetch_calendar_data
    puts "\nFetching calendar data..."
    calendar = Calendar::CalendarService.new
    calendar.client_options.application_name = APPLICATION_NAME
    calendar.authorization = authorize

    events = calendar.list_events(
      'primary',
      max_results: 100,
      single_events: true,
      order_by: 'startTime',
      time_min: DateTime.now.rfc3339
    )

    output_file = File.join(@data_dir, 'calendar_data.json')
    File.open(output_file, 'w') do |file|
      file.write(JSON.pretty_generate(events.to_h))
    end
    puts "✅ Calendar data saved to #{output_file}"
    puts "   Found #{events.items.length} upcoming events"
  rescue Google::Apis::AuthorizationError => e
    puts "❌ Authorization Error: #{e.message}"
    puts "Please delete #{TOKEN_PATH} and try again."
  rescue Google::Apis::ClientError => e
    puts "❌ Client Error: #{e.message}"
  rescue StandardError => e
    puts "❌ Error: #{e.message}"
  end

  def fetch_contacts_data
    puts "\nFetching contacts data..."
    people = People::PeopleServiceService.new
    people.client_options.application_name = APPLICATION_NAME
    people.authorization = authorize

    response = people.list_person_connections(
      'people/me',
      page_size: 100,
      person_fields: 'names,emailAddresses,phoneNumbers,addresses'
    )

    output_file = File.join(@data_dir, 'contacts_data.json')
    File.open(output_file, 'w') do |file|
      file.write(JSON.pretty_generate(response.to_h))
    end
    puts "✅ Contacts data saved to #{output_file}"
    puts "   Found #{response.connections&.length || 0} contacts"
  rescue Google::Apis::AuthorizationError => e
    puts "❌ Authorization Error: #{e.message}"
    puts "Please delete #{TOKEN_PATH} and try again."
  rescue Google::Apis::ClientError => e
    puts "❌ Client Error: #{e.message}"
  rescue StandardError => e
    puts "❌ Error: #{e.message}"
  end

  private

  def authorize
    client_id = Google::Auth::ClientId.from_file(CREDENTIALS_PATH)
    token_store = Google::Auth::Stores::FileTokenStore.new(file: TOKEN_PATH)
    authorizer = Google::Auth::UserAuthorizer.new(client_id, SCOPES, token_store)
    user_id = 'default'

    credentials = authorizer.get_credentials(user_id)
    if credentials.nil?
      credentials = handle_oauth_flow(authorizer, user_id)
    else
      puts "✅ Using stored credentials"
    end
    credentials
  end

  def handle_oauth_flow(authorizer, user_id)
    puts "\n🔐 Starting OAuth authorization flow..."
    
    @server = WEBrick::HTTPServer.new(
      Port: PORT,
      AccessLog: [],
      Logger: WEBrick::Log.new(nil, 0)
    )

    @server.mount_proc '/oauth2callback' do |req, res|
      @received_code = req.query['code']
      res.body = "Authorization code received! You can close this window and return to the terminal."
      Thread.new { @server.shutdown }
    end

    auth_url = authorizer.get_authorization_url(
      base_url: "http://localhost:#{PORT}/oauth2callback",
      access_type: 'offline',
      prompt: 'consent'
    )

    puts "\n📱 Please authorize the application:"
    puts "\n1. Copy this URL and paste it into your browser:"
    puts "\n   #{auth_url}"
    puts "\n2. Follow the prompts to authorize the application"
    puts "\n3. Wait for the success message in your browser"

    trap('INT') { @server.shutdown }
    @server.start

    if @received_code
      puts "\n✅ Authorization code received!"
      credentials = authorizer.get_and_store_credentials_from_code(
        user_id: user_id,
        code: @received_code,
        base_url: "http://localhost:#{PORT}/oauth2callback"
      )
      puts "✅ Credentials stored successfully!"
      credentials
    else
      puts "\n❌ Failed to receive authorization code"
      nil
    end
  end
end

def parse_options
  if ARGV.include?('--help') || ARGV.include?('-h')
    puts "Usage: google_data_fetcher.rb [options]"
    puts "Options:"
    puts "  --all, -a     Fetch all data (calendar and contacts)"
    puts "  --calendar, -c  Fetch calendar data only"
    puts "  --contacts, -t  Fetch contacts data only"
    puts "  --help, -h     Show this help message"
    exit
  end

  {
    all: ARGV.include?('--all') || ARGV.include?('-a'),
    calendar: ARGV.include?('--calendar') || ARGV.include?('-c'),
    contacts: ARGV.include?('--contacts') || ARGV.include?('-t')
  }
end

def main
  # Create data directory if it doesn't exist
  FileUtils.mkdir_p(DATA_DIR)

  # Parse command line options
  options = parse_options

  # Show welcome message
  puts "\n🚀 Google Data Fetcher"
  puts "===================="
  puts "This script will fetch your Google Calendar and/or Contacts data."
  puts "Make sure you have placed your OAuth credentials.json file in:"
  puts CREDENTIALS_PATH
  puts "\nPress Enter to continue (Ctrl+C to cancel)..."
  
  STDIN.gets

  # Create fetcher instance
  fetcher = GoogleDataFetcher.new

  # Execute based on options
  if options[:all] || (options.empty? && ARGV.empty?)
    puts "\nFetching all data..."
    fetcher.fetch_calendar_data
    fetcher.fetch_contacts_data
  elsif options[:calendar]
    puts "\nFetching calendar data only..."
    fetcher.fetch_calendar_data
  elsif options[:contacts]
    puts "\nFetching contacts data only..."
    fetcher.fetch_contacts_data
  else
    puts "No valid options provided. Use --help for usage information."
  end
end

# Run the main program
begin
  main
rescue Interrupt
  puts "\n\nScript cancelled by user."
  exit 1
rescue StandardError => e
  puts "\n❌ Error: #{e.message}"
  puts e.backtrace
  exit 1
end