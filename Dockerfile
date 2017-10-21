FROM python:3.6-onbuild

# Set aws environment variables
ENV AWS_ACCESS_KEY_ID AKIAJPMK7AM435FHNTBQ
ENV AWS_SECRET_ACCESS_KEY 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
ENV AWS_DEFAULT_REGION us-east-1

#
RUN aws lex-models get-slot-type --name FlowerTypes --slot-type-version "\$LATEST"
RUN aws lex-models create-slot-type-version --name FlowerTypes --checksum "checksum"
# RUN aws lex-models put-bot-alias --name PROD --bot-name OrderFlowersBot --bot-version 0.0.1