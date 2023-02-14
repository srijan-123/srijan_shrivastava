import os, csv
import pandas as pd

import langid
import googleapiclient.discovery


def setup_init():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # YOUR_API_KEY = AIzaSyC8aUtdCpsAuEbTnnqH9YyftynTOXkBAJE
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyC8aUtdCpsAuEbTnnqH9YyftynTOXkBAJE"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    return youtube

def get_search_response(youtube, query, part="id,snippet", type_video="video", maxResults=5, \
    publishedAfter=None, publishedBefore=None):

    request_search = youtube.search().list(
        part=part,
        type=type_video,
        q=query,
        maxResults=maxResults,
        publishedAfter = publishedAfter, 
        publishedBefore = publishedBefore
    )
    # Request execution
    response_search = request_search.execute()

    return response_search

def get_comment_response(youtube, videoId, part="id,snippet,replies", maxResults=50, order="relevance"):   

    request_comments = youtube.commentThreads().list(
            part=part,
            videoId=videoId,
            maxResults=maxResults,
            order=order
        )
    response = request_comments.execute()

    return response

def is_english_comment(text):
    detected_lang = langid.classify(text)

    if detected_lang[0] == 'en':
        return True
    else:
        return False    

def main():

    youtube = setup_init()

    #Fetching search results
    search_query = "#Khalistan"
    response_search = get_search_response(youtube, query=search_query, maxResults=5, publishedAfter=None, publishedBefore=None)


    textDisplay_value, textOriginal_value = [], []
    authorDisplayName_value, authorChannelId_value = [], []
    publishedAt_value, videoId_value = [], []

    for i in range(len(response_search["items"])):
        videoId_temp = str(response_search["items"][i]["id"]["videoId"])

        #Fetching comments from search videos
        try:
            response_comments = get_comment_response(youtube, videoId=videoId_temp )
        except Exception as E:
            print("Exception occured", E)

        for j in range(len(response_comments["items"])):


            textOriginal_temp = response_comments['items'][j]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            eng_comment = is_english_comment(textOriginal_temp)

            if (eng_comment):

                textOriginal_value.append(textOriginal_temp)

                textDisplay_temp = response_comments['items'][j]["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                textDisplay_value.append(textDisplay_temp)

                authorDisplayName_temp = response_comments['items'][j]["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                authorDisplayName_value.append(authorDisplayName_temp)

                authorChannelId_temp = response_comments['items'][j]["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]['value']
                authorChannelId_value.append(authorChannelId_temp)

                publishedAt_temp = response_comments['items'][j]["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                publishedAt_value.append(publishedAt_temp)

                videoId_value.append(videoId_temp)

                # print(textDisplay_value, authorDisplayName_value, authorChannelId_value, publishedAt_value)


        yt_comments_data = {
        "videoID":videoId_value,
        "textDisplay": textDisplay_value,
        "textOriginal": textOriginal_value,
        "authorDisplayName": authorDisplayName_value,
        "authorChannelId":authorChannelId_value,
        "publishedAt":publishedAt_value,
        }

        # print(yt_comments_data)
        df = pd.DataFrame.from_dict(yt_comments_data) 
        df.to_csv (r'yt_comments_'+str(search_query)+'.csv', index = False, header=True)



main()

# if __name__ == "__main__":
#     main()