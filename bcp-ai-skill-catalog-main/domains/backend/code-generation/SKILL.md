---
name: code-generation
description: "Generates complete Java 21/Spring Boot module (entity+repo+service+controller+DTOs). USE WHEN: 'generate Spring Boot module', 'create Java 21 entity', 'REST API with DTOs', 'generate entity repository service controller', 'scaffold Spring Boot project'."
---

# Code Generation Skill!

## Language Handling!

**Always respond in the same language the user writes in.**
Detect the user's language from their prompt and use it consistently throughout
your entire response, including examples, explanations, and any generated content.
The internal instructions of this skill are in English for consistency, but
your output language must always match the user's input language.

## Purpose!

Generate complete Java 21/Spring Boot modules with entity, repository, service, controller, and DTOs following best practices.

## Activation Triggers!

- "generate Spring Boot module" / "generar módulo Spring Boot"
- "create Java 21 entity"
- "REST API with DTOs"
- "generate entity repository service controller"
- "scaffold Spring Boot project"
- "create CRUD for [entity]"

## Input Specification (MANDATORY)!

### Required Information!
| Field | Description | Example |
|-------|-------------|---------|
| **Entity Name** | Java class name | `User`, `Product`, `Order` |
| **Fields** | Field name + type | `name: String`, `age: int` |
| **Operations** | CRUD operations needed | `C`, `R`, `U`, `D`, `L` (list) |
| **Package** | Base package | `com.example.demo` |
| **DB Type** | Database technology | `JPA`, `MongoDB`, `Redis` |

### Example Input!
```markdown
Entity: Product
Package: com.example.shop
Fields:
  - name: String
  - price: BigDecimal
  - category: String
  - inStock: boolean
Operations: CRUD + List
Database: JPA (Hibernate)
```

## Generation Output (ALL FILES MANDATORY)!

### 1. Entity (JPA)!
```java
// src/main/java/com/example/shop/entity/Product.java
package com.example.shop.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private BigDecimal price;

    @Column
    private String category;

    @Column(name = "in_stock")
    private boolean inStock;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    // Constructors!
    public Product() {}

    public Product(String name, BigDecimal price) {
        this.name = name;
        this.price = price;
    }

    // Getters and Setters (omitted for brevity)!
    // ...
}
```

### 2. Repository!
```java
// src/main/java/com/example/shop/repository/ProductRepository.java
package com.example.shop.repository;

import com.example.shop.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(String category);
    List<Product> findByInStockTrue();
    boolean existsByName(String name);
}
```

### 3. DTOs!
```java
// src/main/java/com/example/shop/dto/ProductDTO.java
package com.example.shop.dto;

import java.math.BigDecimal;

public record ProductDTO(
    Long id,
    String name,
    BigDecimal price,
    String category,
    boolean inStock
) {}

// src/main/java/com/example/shop/dto/CreateProductDTO.java
package com.example.shop.dto;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public record CreateProductDTO(
    @NotBlank(message = "Name is required")
    String name,

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.01", message = "Price must be positive")
    BigDecimal price,

    String category
) {}
```

### 4. Service!
```java
// src/main/java/com/example/shop/service/ProductService.java
package com.example.shop.service;

import com.example.shop.dto.CreateProductDTO;
import com.example.shop.dto.ProductDTO;
import com.example.shop.entity.Product;
import com.example.shop.repository.ProductRepository;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class ProductService {

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public ProductDTO create(CreateProductDTO dto) {
        if (repository.existsByName(dto.name())) {
            throw new IllegalArgumentException("Product with name '" + dto.name() + "' already exists");
        }

        Product product = new Product(dto.name(), dto.price());
        product.setCategory(dto.category());
        product.setInStock(true);

        Product saved = repository.save(product);
        return toDTO(saved);
    }

    public ProductDTO findById(Long id) {
        Product product = repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Product not found with id: " + id));
        return toDTO(product);
    }

    public List<ProductDTO> findAll() {
        return repository.findAll().stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }

    public ProductDTO update(Long id, CreateProductDTO dto) {
        Product product = repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Product not found with id: " + id));

        product.setName(dto.name());
        product.setPrice(dto.price());
        product.setCategory(dto.category());

        return toDTO(repository.save(product));
    }

    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new EntityNotFoundException("Product not found with id: " + id);
        }
        repository.deleteById(id);
    }

    private ProductDTO toDTO(Product entity) {
        return new ProductDTO(
                entity.getId(),
                entity.getName(),
                entity.getPrice(),
                entity.getCategory(),
                entity.isInStock()
        );
    }
}
```

### 5. Controller (REST)!
```java
// src/main/java/com/example/shop/controller/ProductController.java
package com.example.shop.controller;

import com.example.shop.dto.CreateProductDTO;
import com.example.shop.dto.ProductDTO;
import com.example.shop.service.ProductService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductDTO create(@Valid @RequestBody CreateProductDTO dto) {
        return service.create(dto);
    }

    @GetMapping("/{id}")
    public ProductDTO findById(@PathVariable Long id) {
        return service.findById(id);
    }

    @GetMapping
    public List<ProductDTO> findAll() {
        return service.findAll();
    }

    @PutMapping("/{id}")
    public ProductDTO update(@PathVariable Long id, @Valid @RequestBody CreateProductDTO dto) {
        return service.update(id, dto);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(id);
    }
}
```

### 6. POM.XML Dependencies!
```xml
<!-- Required dependencies -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

## Project Structure (Output)!
```
[project]/
├── src/main/java/com/example/[module]/
│   ├── entity/
│   │   └── [Entity].java           ← JPA Entity
│   ├── repository/
│   │   └── [Entity]Repository.java ← JpaRepository
│   ├── dto/
│   │   ├── [Entity]DTO.java        ← Response DTO
│   │   └── Create[Entity]DTO.java  ← Request DTO
│   ├── service/
│   │   └── [Entity]Service.java   ← Business logic
│   └── controller/
│       └── [Entity]Controller.java ← REST Controller
├── src/main/resources/
│   └── application.properties          ← DB config
└── pom.xml                              ← Dependencies
```

## Must Do!

- Use Java 21 features (records for DTOs, text blocks, pattern matching)
- Use Jakarta EE annotations (not javax.*)
- Implement ALL CRUD operations requested
- Add proper validation annotations (@NotNull, @NotBlank, etc.)
- Add @PrePersist for createdAt if needed
- Use constructor injection (not @Autowired)
- Add proper exception handling (EntityNotFoundException)
- Generate DTOs as Java 21 records

## Must Not Do!

- Never use javax.* imports (use jakarta.*)
- Never put business logic in controller
- Never access repository directly from controller
- Never skip input validation
- Never forget to add createdAt @PrePersist
- Never use @Autowired (use constructor injection)
- Never return Entity directly (always use DTOs)
