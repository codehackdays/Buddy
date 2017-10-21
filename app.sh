aws lex-models put-slot-type --name FlowerTypes --cli-input-json file://FlowerTypes.json
aws lex-models put-intent --name OrderFlowers --cli-input-json file://OrderFlowers.json
aws lex-models put-bot --name OrderFlowersBot --cli-input-json file://OrderFlowersBot.json
aws lex-models get-bot --name OrderFlowersBot --version-or-alias "\$LATEST"

# RUN aws lex-runtime post-text --bot-name OrderFlowersBot --bot-alias "\$LATEST" --user-id UserOne --input-text "i would like to order flowers"
# RUN aws lex-runtime post-text --bot-name OrderFlowersBot --bot-alias "\$LATEST" --user-id UserOne --input-text "roses"
# RUN aws lex-runtime post-text --bot-name OrderFlowersBot --bot-alias "\$LATEST" --user-id UserOne --input-text "tuesday"
# RUN aws lex-runtime post-text --bot-name OrderFlowersBot --bot-alias "\$LATEST" --user-id UserOne --input-text "10:00 a.m."
# RUN aws lex-runtime post-text --bot-name OrderFlowersBot --bot-alias "\$LATEST" --user-id UserOne --input-text "yes"