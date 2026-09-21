package com.github.core_server.controller;

import com.github.core_server.payload.request.RagCallBackRequest;
import com.github.core_server.payload.response.RagCallBackResponse;
import com.github.core_server.service.MessageService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/rag")
@AllArgsConstructor
public class RagCallBackController {

    private final MessageService messageService;

    @PostMapping("/callback")
    public ResponseEntity<RagCallBackResponse> callback(
            @RequestBody RagCallBackRequest request
    ) {

        RagCallBackResponse response =
                messageService.getRagResponse(request);

        return ResponseEntity.ok(response);
    }
}
