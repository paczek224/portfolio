package com.example.portfolio;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;

@RestController
@CrossOrigin(origins = {"http://localhost:5173", "http://127.0.0.1:5173"})
public class PortfolioController {
    private final ObjectMapper objectMapper;

    public PortfolioController(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @GetMapping("/api/portfolio")
    public ResponseEntity<JsonNode> portfolio() throws IOException {
        ClassPathResource resource = new ClassPathResource("portfolio.json");
        JsonNode data = objectMapper.readTree(resource.getInputStream());
        return ResponseEntity.ok(data);
    }
}
