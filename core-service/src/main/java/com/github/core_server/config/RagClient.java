package com.github.core_server.config;

import com.github.core_server.payload.request.RagQueryRequest;
import com.github.core_server.payload.response.RagQueryResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class RagClient {

    private final RestClient restClient;
    private final String ragServiceToken;

    public RagClient(
            RestClient ragRestClient,
            @Value("${rag.service-token}") String ragServiceToken
    ) {
        this.restClient = ragRestClient;
        this.ragServiceToken = ragServiceToken;
    }

    public RagQueryResponse sendQuestion(RagQueryRequest request) {
        return restClient.post()
                .uri("/rag/query")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .header(
                        HttpHeaders.AUTHORIZATION,
                        "Bearer " + ragServiceToken
                )
                .body(request)
                .retrieve()
                .body(RagQueryResponse.class);
    }
}
