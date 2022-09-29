const Alexa = require('ask-sdk-core');
const visualizationBackgroundDocument = require('./documents/visualization_background_document.json');
const HELLO_WORLD_TOKEN = 'helloworldToken';

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speechText = 'Welcome, you can ask me to visualize your health. Try saying "How well did I sleep?"';
  
        return handlerInput.responseBuilder
            .speak(speechText)
            .reprompt(speechText)
            .withSimpleCard('Welcome to My Health.', speechText)
            .getResponse();
    }
};


const AskPictureIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AskPictureIntent';
    },

    handle(handlerInput) {
        let speakOutput = 'Here is your sleep quality data.';
        let responseBuilder = handlerInput.responseBuilder;
        if (Alexa.getSupportedInterfaces(handlerInput.requestEnvelope)['Alexa.Presentation.APL']){
            // Add the RenderDocument directive to the responseBuilder
            responseBuilder.addDirective({
                type: 'Alexa.Presentation.APL.RenderDocument',
                token: HELLO_WORLD_TOKEN,
                document: visualizationBackgroundDocument
            });
        }
        else {
            // User's device does not support APL, so tailor the speech to this situation
            speakOutput += " This example would be more interesting on a device with a screen, such as an Echo Show or Fire TV.";
        }
        return responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
  

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
    },

    handle(handlerInput) {
        const speechText = 'You can ask me to visualize your health!';
  
        return handlerInput.responseBuilder
            .speak(speechText)
            .reprompt(speechText)
            .withSimpleCard('You can ask me to visualize your health', speechText)
            .getResponse();
    }
};


const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
            || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },

    handle(handlerInput) {
        const speechText = 'Goodbye!';
  
        return handlerInput.responseBuilder
            .speak(speechText)
            .withSimpleCard('Goodbye!', speechText)
            .withShouldEndSession(true)
            .getResponse();
    }
};
  
  
  
const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        // Any clean-up logic goes here.
        return handlerInput.responseBuilder.getResponse();
    }
};


const ErrorHandler = {
    canHandle() {
        return true;
    },

    handle(handlerInput, error) {
        console.log(`Error handled: ${error.message}`);
  
        return handlerInput.responseBuilder
        .speak('Sorry, I don\'t understand your command. Please say it again.')
        .reprompt('Sorry, I don\'t understand your command. Please say it again.')
        .getResponse();
    }
};


// Lambda handler
let skill;
exports.handler = async function (event, context) {
    console.log(`REQUEST++++${JSON.stringify(event)}`);
    if (!skill) {
        skill = Alexa.SkillBuilders.custom()
        .addRequestHandlers(
            LaunchRequestHandler,
            AskPictureIntentHandler,
            HelpIntentHandler,
            CancelAndStopIntentHandler,
            SessionEndedRequestHandler,
        )
        .addErrorHandlers(ErrorHandler)
        .create();
    }
    const response = await skill.invoke(event, context);
    console.log(`RESPONSE++++${JSON.stringify(response)}`);
    return response;
};


module.exports = {
    LaunchRequestHandler,
    AskPictureIntentHandler,
    HelpIntentHandler,
    CancelAndStopIntentHandler,
    SessionEndedRequestHandler,
    ErrorHandler
}