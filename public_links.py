from flask import Flask, request, redirect, make_response, Blueprint, Response
import gspread
import os


app = Blueprint('public_links', __name__)

if 'credentials.json' not in os.listdir():
    from utils import gen_credentials
    gen_credentials()

gc = gspread.service_account(filename='credentials.json')

links, authors, dates = {}, {}, {}

@app.route("/_refresh/")
def refresh():
    temp_links, temp_authors, temp_dates = {}, {}, {}
    try:
        gsheet = gc.open_by_key(os.environ.get('SHEET_ID'))
        for entry in gsheet.sheet1.get_all_records():
            shortlink = entry['Shortlink']
            temp_links[shortlink] = entry['URL']
            temp_authors[shortlink] = entry['Creator']
            temp_dates[shortlink] = entry['Date']
        global links, authors, dates
        links, authors, dates = temp_links, temp_authors, temp_dates
        return make_response("Links updated.", 200)
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 403:
            return make_response(f'Please share {os.environ.get("SHEET_NAME")} with {os.environ.get("SERVICE_EMAIL")}.', 403) 
        return make_response('Error reading links.', 500)
    except KeyError as e:
        return make_response(f'Please do not modify the column names on the spreadsheet', 403) 
    except Exception as e:
        return make_response("Error reading links.", 500)

@app.route('/<path:shortlink>')
def go(shortlink):
    if shortlink in links:
        if links[shortlink]:
            return redirect(links[shortlink])
        return make_response('Link missing. Please follow the instructions on the spreadsheet.', 403)
    else:
        refresh()
        if shortlink in links:
            return go(shortlink)
        return make_response('Link not found', 404)

@app.route('/preview/<path:shortlink>')
def preview(shortlink):
    if shortlink in links:
        return f'<div> Points to <a href="{links[shortlink]}">{links[shortlink]}</a></div> <div> Created by {authors[shortlink] if authors[shortlink] else "N/A"} on {dates[str(shortlink)] if dates[str(shortlink)] else "N/A"} </div>'
    else:
        refresh()
        if shortlink in links:
            return preview(shortlink)
        return make_response('Link not found', 404)
