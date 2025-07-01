from serpapi import GoogleSearch

params = {
  "engine": "google",
  "q": "Fresh Bagels",
  "location": "Seattle-Tacoma, WA, Washington, United States",
  "hl": "en",
  "gl": "us",
  "google_domain": "google.com",
  "num": "10",
  "start": "10",
  "safe": "active",
  "api_key": "413889eb3d388c48e34e20dd6f24f4ef26dad124e5293ed5f6c34a21c815bec9"
}

search = GoogleSearch(params)
results = search.get_dict()
organic_results = results["organic_results"]
