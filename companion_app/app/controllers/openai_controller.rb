class OpenaiController < ApplicationController
    def recommendations
        preferences = params[:preferences] || ["default"]
        
        prompt = "User preferences: #{preferences.join(', ')}. Based on these preferences, provide a list of 3 takeout restaurant recommendations, each with a brief description."

        client = OpenAI::Client.new(access_token: ENV['OPENAI_API_KEY'])

        response = client.completions(
            parameters: {
                model: "text-davinci-003",
                prompt: prompt,
                max_tokens: 150,
                temperature: 0.7,
                n: 1
            }
        )

        recommendations_text = response.dig("choices", 0, "text").to_s.strip
        @recommendations = recommendations_text.split("\n").reject(&:empty?)

        render :recommendations
    rescue StandardError => e
        flash[:error] = "Error contacting OpenAI: #{e.message}"
        redirect_to root_path
    end
end
