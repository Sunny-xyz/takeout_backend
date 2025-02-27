Rails.application.routes.draw do
  root 'recommendations#new'
  resources :recommendations, only: [:new, :create]
  mount GovukPublishingComponents::Engine, at: "/component-guide" if Rails.env.development?
  
  resources :restaurants, only: [:index, :show]
end
