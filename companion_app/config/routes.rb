Rails.application.routes.draw do
  get "home/index"
  root "home#index"
  resources :recommendations, only: [ :new, :create ]
  mount GovukPublishingComponents::Engine, at: "/component-guide" if Rails.env.development?

  resources :restaurants, only: [ :index, :show ]
end
