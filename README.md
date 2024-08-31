# Music Streaming Platform

## Overview

This project is a simplified music streaming platform with a REST API for interaction. The platform supports three user types: Consumers, Artists, and Administrators.

## User Types

1. **Consumer**: 
   - **Regular**: Free access.
   - **Premium**: Paid subscription, can create public and private playlists.
   - Consumers can transition between regular and premium statuses. Subscription history is maintained.

2. **Artist**: 
   - Can publish songs and albums.
   - Has attributes like artistic name and relationships with labels.

3. **Administrator**: 
   - Manages artists and generates pre-paid cards for subscriptions.

## Key Features

- **Subscription Plans**: 
  - Paid via pre-paid cards (10, 25, or 50 euros).
  - Plans: Monthly (7 euros), Quarterly (21 euros), or Semesterly (42 euros).
  - Users can use multiple cards and the system tracks card usage.

- **Playlists**:
  - Premium users can create and manage playlists (public or private).
  - Private playlists are inaccessible if the user reverts to regular status.

- **Comments**:
  - Users can comment on songs, and replies are supported.

- **Top 10 Playlist**:
  - Updated based on the last 30 days' playback history using triggers.

- **Reports**:
  - Monthly reports on songs played and genres.

## API Endpoints

- **User Registration**: 
  - `POST /dbproj/user`
  
- **User Authentication**: 
  - `PUT /dbproj/user`

- **Add Song**: 
  - `POST /dbproj/song`

- **Add Album**: 
  - `POST /dbproj/album`

- **Search Song**: 
  - `GET /dbproj/song/{keyword}`

- **Detail Artist**: 
  - `GET /dbproj/artist_info/{artist_id}`

- **Subscribe to Premium**: 
  - `POST /dbproj/subscription`

- **Create Playlist**: 
  - `POST /dbproj/playlist`

- **Play Song**: 
  - `PUT /dbproj/{song_id}`

- **Generate Pre-paid Cards**: 
  - `POST /dbproj/card`

- **Leave Comment/Feedback**: 
  - `POST /dbproj/comments/{song_id}`
  - `POST /dbproj/comments/{song_id}/{parent_comment_id}`

- **Generate Monthly Report**: 
  - `GET /dbproj/report/{year-month}`

## Technical Details

- **Database**: Designed to handle storage and retrieval based on described functionalities.
- **API Interaction**: JSON format for request and response.
- **HTTP Methods**: GET, POST, PUT.
- **Error Handling**: Standard HTTP status codes (200, 400, 500).
