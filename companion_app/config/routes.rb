Rails.application.routes.draw do
  root 'recommendations#new'
  resources :recommendations, only: [:new, :create]
end
