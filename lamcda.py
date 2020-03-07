from __future__ import print_function
import random 

# --------------- Helpers that build all of the responses ----------------------



def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    session_attributes = {
        "state":0,
        "qn":0,
        "hint":0,
        "items":["tree","bottle","paper"],
        "hints":[["I live in forest","I am scared of axe","I have brown body and green face."],["I am a kind of container","I am non biodegradable","I store liquids"],["I am biodegradable","People use me to note down things"]]
    }
    card_title = "Welcome"
    speech_output = "Welcome to Reverse Akinator! Do you want to here the rules?"
    reprompt_text = "I don't know if you heard me, welcome to your Green mafia!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_rules_response(intent , session):
    session_attributes = session['attributes']
    card_title = "Rules"
    if intent["slots"]["yn"].get("value")==None:
        speech_output = "Sorry I am unable to catch that please respond in yes or no."
    else :
        session_attributes["state"] = 1
        if intent["slots"]["yn"].get("value") == "yes":
            speech_output = "These are the rules. Tell me yes when you are ready"
        else:
            speech_output = "Ok lets start the game. Tell me yes when you are ready."
    reprompt_text = "I don't know if you heard me, Please tell me do you want to here rules?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def start_new_item(intent,session):
    session_attributes = session['attributes']
    card_title = "Start New Item"
    if intent["slots"]["yn"].get("value")==None:
        speech_output = "Sorry I am unable to catch that please respond in yes or no."
    else:
        if intent["slots"]["yn"].get("value") == "yes":
            cq=session_attributes["qn"]
            h=session_attributes["hint"]
            speech_output="Ok. Starting with new item. Here is your first hint. "+session_attributes["hints"][cq][h]
            session_attributes["state"]=2
            session_attributes["hint"]+=1
        else:
            speech_output="Waiting for your yes."
    reprompt_text = "I don't know if you heard me, Please tell me something"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def continue_game(intent,session):
    session_attributes = session['attributes']
    card_title = "Continue with current item"
    cq=session_attributes["qn"]
    h=session_attributes["hint"]
    if intent["slots"]["yn"].get("value")==None:
        ans=intent["slots"]["answer"].get("value")
        if ans=="pass":
            speech_output="Ok. I am telling you the right answer. The right answer is "+session_attributes["items"][cq]+" Tell me yes to go to next item in my bag."
            session_attributes["state"]=1            
            session_attributes["qn"]+=1
            session_attributes["hint"]=0
        elif ans==session_attributes["items"][cq]:
            speech_output="Hurrah! You have answered correctly. Tell me yes to go to next item in my bag."
            session_attributes["state"]=1            
            session_attributes["qn"]+=1
            session_attributes["hint"]=0
        else:
            speech_output="Uh Oh! Wrong answer. Do you want a hint?"
    else:
        if intent["slots"]["yn"].get("value")=="yes":
            if h<len(session_attributes["hints"][cq]):
                speech_output="Here is the next hint. "+session_attributes["hints"][cq][h]
                session_attributes["hint"]+=1
            else:
                speech_output="Sorry I am out of hints. Either make a guess or pass"
        else:
            speech_output="Sorry. Say yes for hint or try to make a guess."
    reprompt_text = "I don't know if you heard me, Please tell me something"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you Playing Green Mafia " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    session["state"] = 0
    session["qn"]=0
    session["hint"]=0
    session["items"]=["tree","bottle","paper"]
    session["hints"]=[["I live in forest","I am scared of axe","I have brown body and green face."],
                      ["I am a kind of container","I am non biodegradable","I store liquids"],
                      ["I am biodegradable","People use me to note down things"]
                     ]

def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    if intent_name == "FirstIntent":
        if session["attributes"]["state"] == 0:
            return get_rules_response(intent , session)
        elif session["attributes"]["state"]==1:
            return start_new_item(intent,session)
        elif session["attributes"]["state"]==2:
            return continue_game(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):

    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        #return on_session_ended(event['request'], event['session'])
        return handle_session_end_request()
