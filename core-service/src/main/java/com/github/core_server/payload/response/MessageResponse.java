package com.github.core_server.payload.response;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Builder
public class MessageResponse {
    private String content;
    private String sendTime;
    private String messageId;
    private String conversationId;
    private String sources;
    private String status;
    private boolean botMessage;
}
