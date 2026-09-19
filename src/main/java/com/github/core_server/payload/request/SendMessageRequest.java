package com.github.core_server.payload.request;

import lombok.Getter;

@Getter
public class SendMessageRequest {
    private String conversationId;
    private String content;
}
