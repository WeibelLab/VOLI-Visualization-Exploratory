const Alexa = require('ask-sdk-core');
const handlers = require('./handlers');

console.log("========== hello world ============");

try {
    exports.handler = Alexa.SkillBuilders.custom()
        .addRequestHandlers(
            handlers.LaunchRequestHandler,
            handlers.AskPictureIntentHandler,
            handlers.HelpIntentHandler,
            handlers.CancelAndStopIntentHandler,
            handlers.SessionEndedHandler)
        .addErrorHandlers(handlers.ErrorHandler)
        .lambda();
} 
catch (err) {
    console.log("======= building skills =======");
    console.log(err);
}