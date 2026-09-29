package com.github.core_server.payload.request;

import com.github.core_server.dto.RagSourceDto;
import lombok.Getter;

import java.util.List;

@Getter
public class RagCallBackRequest {
    private String conversationId;
    private String answer;
    private List<RagSourceDto> sources;
}
