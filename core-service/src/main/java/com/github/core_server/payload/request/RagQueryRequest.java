package com.github.core_server.payload.request;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Builder
public class RagQueryRequest {
    private String conversationId;
    private String question;
}
