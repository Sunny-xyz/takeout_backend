class RecommendationsController < ApplicationController
    require 'httparty'

    def new; end

    def create
        preferences = params[:preferences]
        pref_array = preferences.split(',').map(&:strip)
        
        payload = { preferences: pref_array }

        response = HTTParty.post("http://127.0.0.1:8000/recommendations",
        body: payload.to_json,
        headers: { 'Content-Type' => 'application/json' })


        if response.success?
            @recommendations = response.parsed_response["recommendations"]
        else
            @recommendations = ["Error fetching recommendations"]
        end

      render :new
    end
  end
