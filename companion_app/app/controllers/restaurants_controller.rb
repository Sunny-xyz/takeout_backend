class RestaurantsController < ApplicationController
    require "httparty"

def index
  begin
    response = HTTParty.get("http://127.0.0.1:8002/restaurants")
    Rails.logger.debug "Restaurant API raw response: #{response.parsed_response.inspect}"
    @raw_response = response.parsed_response
  rescue => e
    Rails.logger.error("Error fetching restaurants: #{e.message}")
    @raw_response = { error: "Error fetching restaurants: #{e.message}" }
    flash.now[:alert] = "Error fetching restaurants"
  end
end



def show
    restaurant_id = params[:id]
    begin
        response = HTTParty.get("http://127.0.0.1:8002/restaurants/#{restaurant_id}")
        response.raise_for_status
        @restaurant = response.parsed_response
    rescue => e
        Rails.logger.error("Error fetching restaurant details: #{e.message}")
        @restaurant = nil
        flash.now[:alert] = "Error fetching restaurant details"
      end
    end
end
