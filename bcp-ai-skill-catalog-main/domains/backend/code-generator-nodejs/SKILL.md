# code-generator-nodejs-nestjs

> **Versión**: 1.0.0  
> **Fase**: Phase 2 - Development (Backend)  
> **Tipo**: Backend Code Generation - Node.js + NestJS  
> **Stack**: NestJS 10, TypeScript 5, TypeORM 0.3, PostgreSQL, Jest 29

---

## 📖 Descripción

**Generador completo de backend NestJS 10 + TypeScript** desde contratos OpenAPI 3.0 o implementation specs. Genera controllers, services, DTOs, entities TypeORM, validations, exception handling, tests Jest, y configuración completa.

**Enfoque API-First**: Consume contrato OpenAPI para generar:
- ✅ Controllers RESTful con decoradores NestJS
- ✅ Services con lógica de negocio
- ✅ DTOs con class-validator validations
- ✅ Entities TypeORM con relaciones
- ✅ Repositories y custom queries
- ✅ Exception filters globales
- ✅ Guards de autenticación (JWT)
- ✅ Tests unitarios con Jest (≥80% coverage)
- ✅ Configuración environment (ConfigModule)
- ✅ Documentación Swagger automática

---

## 🎯 Casos de Uso

Este skill es ideal cuando necesitas:

1. **Generar backend NestJS desde contrato OpenAPI** (API-First)
2. **CRUD completo** con TypeORM + PostgreSQL
3. **Type-safe backend** con TypeScript end-to-end
4. **Modern Node.js patterns** (Dependency Injection, Modules)
5. **Production-ready setup** (validation, auth, error handling)
6. **Testing setup** completo desde el inicio

---

## ✅ Prerequisitos

**Entradas requeridas**:
1. **Contrato OpenAPI 3.0** (openapi-contract.yaml) **O**
2. **Implementation Spec** (implementation-spec.md)
3. *Opcional*: Database schema description

**Stack requerido**:
```json
{
  "@nestjs/core": "^10.0.0",
  "@nestjs/common": "^10.0.0",
  "@nestjs/platform-express": "^10.0.0",
  "@nestjs/typeorm": "^10.0.0",
  "@nestjs/swagger": "^7.0.0",
  "@nestjs/jwt": "^10.0.0",
  "@nestjs/config": "^3.0.0",
  "typeorm": "^0.3.0",
  "pg": "^8.11.0",
  "class-validator": "^0.14.0",
  "class-transformer": "^0.5.1",
  "typescript": "^5.3.0"
}
```

---

## 🚀 Uso

### Invocación Básica

```
@code-generator-nodejs-nestjs genera backend NestJS desde:

**OpenAPI Contract**: [ruta al openapi-contract.yaml]

**O**

**Implementation Spec**: [ruta al implementation-spec.md]

**Database**: PostgreSQL

**Features requeridas**:
- CRUD completo para [Resource1]
- Autenticación JWT
- Validación de DTOs
- Swagger documentation
- Unit tests con Jest
```

### Ejemplo Completo: E-commerce Product API

```
@code-generator-nodejs-nestjs genera backend NestJS desde:

**OpenAPI Contract**: ./openapi-contract.yaml

**Database**: PostgreSQL

**Features requeridas**:
- CRUD completo para productos
- Búsqueda y filtros por categoría y precio
- Paginación en listados
- Validación de datos (price > 0, stock >= 0)
- Autenticación JWT para operaciones protegidas
- Role-based access (admin vs usuario)
- Swagger documentation automática
- Unit tests ≥80% coverage

**Entidades**:
- Product: id, name, description, price, stock, category, createdAt, updatedAt
- Category: id, name, description
- Relación: Product.category → Category (Many-to-One)

**Extras**:
- Soft deletes
- Audit fields (createdBy, updatedBy)
- Query builders para búsquedas complejas
- DTOs separados (CreateProductDto, UpdateProductDto, ProductResponseDto)
```

---

## 🔧 Workflow Interno del Skill

### STEP 1: Análisis del Contrato OpenAPI o Implementation Spec

**Objetivo**: Extraer información para generar código NestJS.

**Acciones**:
1. **Leer contrato OpenAPI**:
   ```bash
   read_file openapi-contract.yaml
   ```

2. **Extraer recursos y schemas**:
   ```typescript
   // De paths extraer recursos
   /products → ProductsModule, ProductsController, ProductsService
   /products/{id} → CRUD operations
   
   // De components.schemas generar entities y DTOs
   Product → ProductEntity, CreateProductDto, UpdateProductDto, ProductResponseDto
   ```

3. **Mapear operaciones a métodos**:
   ```typescript
   GET /products → @Get() findAll()
   GET /products/:id → @Get(':id') findOne(@Param('id') id: string)
   POST /products → @Post() create(@Body() createDto: CreateProductDto)
   PUT /products/:id → @Put(':id') update(@Param('id') id: string, @Body() updateDto: UpdateProductDto)
   DELETE /products/:id → @Delete(':id') remove(@Param('id') id: string)
   ```

4. **Identificar relaciones**:
   ```typescript
   // De $ref en schemas detectar relaciones
   Product.category → @ManyToOne(() => Category)
   Category.products → @OneToMany(() => Product)
   ```

---

### STEP 2: Generación de Estructura del Proyecto

**Objetivo**: Crear estructura modular NestJS.

**Estructura generada**:

```
backend/
├── src/
│   ├── modules/                  # Feature modules
│   │   ├── products/
│   │   │   ├── dto/
│   │   │   │   ├── create-product.dto.ts
│   │   │   │   ├── update-product.dto.ts
│   │   │   │   ├── product-response.dto.ts
│   │   │   │   └── product-filters.dto.ts
│   │   │   ├── entities/
│   │   │   │   └── product.entity.ts
│   │   │   ├── products.controller.ts
│   │   │   ├── products.service.ts
│   │   │   ├── products.module.ts
│   │   │   └── products.controller.spec.ts
│   │   │   └── products.service.spec.ts
│   │   │
│   │   ├── categories/
│   │   │   └── [similar structure]
│   │   │
│   │   └── auth/
│   │       ├── dto/
│   │       │   ├── login.dto.ts
│   │       │   └── register.dto.ts
│   │       ├── guards/
│   │       │   ├── jwt-auth.guard.ts
│   │       │   └── roles.guard.ts
│   │       ├── strategies/
│   │       │   └── jwt.strategy.ts
│   │       ├── auth.controller.ts
│   │       ├── auth.service.ts
│   │       └── auth.module.ts
│   │
│   ├── common/                   # Shared code
│   │   ├── decorators/
│   │   │   ├── roles.decorator.ts
│   │   │   └── current-user.decorator.ts
│   │   ├── filters/
│   │   │   └── http-exception.filter.ts
│   │   ├── interceptors/
│   │   │   └── transform.interceptor.ts
│   │   ├── pipes/
│   │   │   └── validation.pipe.ts
│   │   └── interfaces/
│   │       └── pagination.interface.ts
│   │
│   ├── config/                   # Configuration
│   │   ├── database.config.ts
│   │   └── jwt.config.ts
│   │
│   ├── app.module.ts
│   ├── main.ts
│   └── app.controller.spec.ts
│
├── test/
│   └── app.e2e-spec.ts
│
├── .env.example
├── .gitignore
├── nest-cli.json
├── package.json
├── tsconfig.json
├── tsconfig.build.json
└── README.md
```

---

### STEP 3: Generación de Entities (TypeORM)

**Objetivo**: Entities TypeORM desde OpenAPI schemas.

**Archivo**: `src/modules/products/entities/product.entity.ts`

```typescript
import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, CreateDateColumn, UpdateDateColumn, DeleteDateColumn } from 'typeorm';
import { Category } from '../../categories/entities/category.entity';

@Entity('products')
export class Product {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ length: 255 })
  name: string;

  @Column('text')
  description: string;

  @Column('decimal', { precision: 10, scale: 2 })
  price: number;

  @Column('int', { default: 0 })
  stock: number;

  @ManyToOne(() => Category, (category) => category.products, { nullable: false })
  category: Category;

  @Column({ length: 500, nullable: true })
  imageUrl: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @DeleteDateColumn()
  deletedAt: Date;
}
```

---

### STEP 4: Generación de DTOs (class-validator)

**Objetivo**: DTOs type-safe con validaciones.

**Archivo**: `src/modules/products/dto/create-product.dto.ts`

```typescript
import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsNumber, IsUUID, Min, MaxLength, IsOptional, IsUrl } from 'class-validator';

export class CreateProductDto {
  @ApiProperty({ example: 'Laptop Dell XPS 15', description: 'Product name' })
  @IsString()
  @MaxLength(255)
  name: string;

  @ApiProperty({ example: 'High-performance laptop with 16GB RAM', description: 'Product description' })
  @IsString()
  description: string;

  @ApiProperty({ example: 1299.99, description: 'Product price' })
  @IsNumber()
  @Min(0)
  price: number;

  @ApiProperty({ example: 50, description: 'Available stock quantity' })
  @IsNumber()
  @Min(0)
  stock: number;

  @ApiProperty({ example: '550e8400-e29b-41d4-a716-446655440000', description: 'Category UUID' })
  @IsUUID()
  categoryId: string;

  @ApiProperty({ example: 'https://example.com/image.jpg', required: false })
  @IsOptional()
  @IsUrl()
  imageUrl?: string;
}
```

**Archivo**: `src/modules/products/dto/update-product.dto.ts`

```typescript
import { PartialType } from '@nestjs/swagger';
import { CreateProductDto } from './create-product.dto';

export class UpdateProductDto extends PartialType(CreateProductDto) {}
```

**Archivo**: `src/modules/products/dto/product-response.dto.ts`

```typescript
import { ApiProperty } from '@nestjs/swagger';
import { Exclude, Expose, Type } from 'class-transformer';
import { CategoryResponseDto } from '../../categories/dto/category-response.dto';

@Exclude()
export class ProductResponseDto {
  @Expose()
  @ApiProperty()
  id: string;

  @Expose()
  @ApiProperty()
  name: string;

  @Expose()
  @ApiProperty()
  description: string;

  @Expose()
  @ApiProperty()
  price: number;

  @Expose()
  @ApiProperty()
  stock: number;

  @Expose()
  @Type(() => CategoryResponseDto)
  @ApiProperty({ type: CategoryResponseDto })
  category: CategoryResponseDto;

  @Expose()
  @ApiProperty()
  imageUrl: string;

  @Expose()
  @ApiProperty()
  createdAt: Date;

  @Expose()
  @ApiProperty()
  updatedAt: Date;
}
```

---

### STEP 5: Generación de Services

**Objetivo**: Business logic en services con TypeORM repositories.

**Archivo**: `src/modules/products/products.service.ts`

```typescript
import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere, Like } from 'typeorm';
import { Product } from './entities/product.entity';
import { CreateProductDto } from './dto/create-product.dto';
import { UpdateProductDto } from './dto/update-product.dto';
import { ProductFiltersDto } from './dto/product-filters.dto';
import { PaginatedResponse } from '../../common/interfaces/pagination.interface';

@Injectable()
export class ProductsService {
  constructor(
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
  ) {}

  async findAll(filters: ProductFiltersDto): Promise<PaginatedResponse<Product>> {
    const { page = 1, limit = 20, search, categoryId, minPrice, maxPrice } = filters;
    const skip = (page - 1) * limit;

    const where: FindOptionsWhere<Product> = {};

    if (search) {
      where.name = Like(`%${search}%`);
    }

    if (categoryId) {
      where.category = { id: categoryId };
    }

    const queryBuilder = this.productRepository.createQueryBuilder('product')
      .leftJoinAndSelect('product.category', 'category')
      .where(where);

    if (minPrice !== undefined) {
      queryBuilder.andWhere('product.price >= :minPrice', { minPrice });
    }

    if (maxPrice !== undefined) {
      queryBuilder.andWhere('product.price <= :maxPrice', { maxPrice });
    }

    const [data, total] = await queryBuilder
      .skip(skip)
      .take(limit)
      .orderBy('product.createdAt', 'DESC')
      .getManyAndCount();

    return {
      data,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string): Promise<Product> {
    const product = await this.productRepository.findOne({
      where: { id },
      relations: ['category'],
    });

    if (!product) {
      throw new NotFoundException(`Product with ID ${id} not found`);
    }

    return product;
  }

  async create(createProductDto: CreateProductDto): Promise<Product> {
    const product = this.productRepository.create({
      ...createProductDto,
      category: { id: createProductDto.categoryId },
    });

    try {
      return await this.productRepository.save(product);
    } catch (error) {
      if (error.code === '23503') { // Foreign key violation
        throw new BadRequestException('Category not found');
      }
      throw error;
    }
  }

  async update(id: string, updateProductDto: UpdateProductDto): Promise<Product> {
    const product = await this.findOne(id);

    if (updateProductDto.categoryId) {
      product.category = { id: updateProductDto.categoryId } as any;
    }

    Object.assign(product, updateProductDto);

    try {
      return await this.productRepository.save(product);
    } catch (error) {
      if (error.code === '23503') {
        throw new BadRequestException('Category not found');
      }
      throw error;
    }
  }

  async remove(id: string): Promise<void> {
    const product = await this.findOne(id);
    await this.productRepository.softRemove(product);
  }
}
```

---

### STEP 6: Generación de Controllers

**Objetivo**: RESTful controllers con Swagger decorators.

**Archivo**: `src/modules/products/products.controller.ts`

```typescript
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
  ParseUUIDPipe,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { ProductsService } from './products.service';
import { CreateProductDto } from './dto/create-product.dto';
import { UpdateProductDto } from './dto/update-product.dto';
import { ProductResponseDto } from './dto/product-response.dto';
import { ProductFiltersDto } from './dto/product-filters.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { Roles } from '../../common/decorators/roles.decorator';
import { RolesGuard } from '../auth/guards/roles.guard';
import { plainToInstance } from 'class-transformer';

@ApiTags('products')
@Controller('products')
export class ProductsController {
  constructor(private readonly productsService: ProductsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all products with pagination and filters' })
  @ApiResponse({ status: 200, description: 'Products retrieved successfully', type: [ProductResponseDto] })
  async findAll(@Query() filters: ProductFiltersDto) {
    const result = await this.productsService.findAll(filters);
    return {
      ...result,
      data: plainToInstance(ProductResponseDto, result.data),
    };
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get product by ID' })
  @ApiResponse({ status: 200, description: 'Product retrieved successfully', type: ProductResponseDto })
  @ApiResponse({ status: 404, description: 'Product not found' })
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    const product = await this.productsService.findOne(id);
    return plainToInstance(ProductResponseDto, product);
  }

  @Post()
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('admin')
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Create a new product (admin only)' })
  @ApiResponse({ status: 201, description: 'Product created successfully', type: ProductResponseDto })
  @ApiResponse({ status: 400, description: 'Invalid input' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden' })
  async create(@Body() createProductDto: CreateProductDto) {
    const product = await this.productsService.create(createProductDto);
    return plainToInstance(ProductResponseDto, product);
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('admin')
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update product by ID (admin only)' })
  @ApiResponse({ status: 200, description: 'Product updated successfully', type: ProductResponseDto })
  @ApiResponse({ status: 404, description: 'Product not found' })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() updateProductDto: UpdateProductDto,
  ) {
    const product = await this.productsService.update(id, updateProductDto);
    return plainToInstance(ProductResponseDto, product);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('admin')
  @ApiBearerAuth()
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete product by ID (admin only)' })
  @ApiResponse({ status: 204, description: 'Product deleted successfully' })
  @ApiResponse({ status: 404, description: 'Product not found' })
  async remove(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    await this.productsService.remove(id);
  }
}
```

---

### STEP 7: Generación de Module

**Archivo**: `src/modules/products/products.module.ts`

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ProductsController } from './products.controller';
import { ProductsService } from './products.service';
import { Product } from './entities/product.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Product])],
  controllers: [ProductsController],
  providers: [ProductsService],
  exports: [ProductsService],
})
export class ProductsModule {}
```

---

### STEP 8: Generación de Tests

**Objetivo**: Unit tests con Jest (≥80% coverage).

**Archivo**: `src/modules/products/products.service.spec.ts`

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { NotFoundException } from '@nestjs/common';
import { ProductsService } from './products.service';
import { Product } from './entities/product.entity';
import { CreateProductDto } from './dto/create-product.dto';

describe('ProductsService', () => {
  let service: ProductsService;
  let repository: Repository<Product>;

  const mockRepository = {
    create: jest.fn(),
    save: jest.fn(),
    findOne: jest.fn(),
    createQueryBuilder: jest.fn(() => ({
      leftJoinAndSelect: jest.fn().mockReturnThis(),
      where: jest.fn().mockReturnThis(),
      andWhere: jest.fn().mockReturnThis(),
      skip: jest.fn().mockReturnThis(),
      take: jest.fn().mockReturnThis(),
      orderBy: jest.fn().mockReturnThis(),
      getManyAndCount: jest.fn(),
    })),
    softRemove: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ProductsService,
        {
          provide: getRepositoryToken(Product),
          useValue: mockRepository,
        },
      ],
    }).compile();

    service = module.get<ProductsService>(ProductsService);
    repository = module.get<Repository<Product>>(getRepositoryToken(Product));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('should create a new product', async () => {
      const createDto: CreateProductDto = {
        name: 'Test Product',
        description: 'Test description',
        price: 99.99,
        stock: 10,
        categoryId: '123e4567-e89b-12d3-a456-426614174000',
      };

      const expectedProduct = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        ...createDto,
        category: { id: createDto.categoryId },
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockRepository.create.mockReturnValue(expectedProduct);
      mockRepository.save.mockResolvedValue(expectedProduct);

      const result = await service.create(createDto);

      expect(repository.create).toHaveBeenCalledWith({
        ...createDto,
        category: { id: createDto.categoryId },
      });
      expect(repository.save).toHaveBeenCalledWith(expectedProduct);
      expect(result).toEqual(expectedProduct);
    });
  });

  describe('findOne', () => {
    it('should return a product by ID', async () => {
      const productId = '123e4567-e89b-12d3-a456-426614174000';
      const expectedProduct = {
        id: productId,
        name: 'Test Product',
        price: 99.99,
        category: { id: '123', name: 'Test Category' },
      };

      mockRepository.findOne.mockResolvedValue(expectedProduct);

      const result = await service.findOne(productId);

      expect(repository.findOne).toHaveBeenCalledWith({
        where: { id: productId },
        relations: ['category'],
      });
      expect(result).toEqual(expectedProduct);
    });

    it('should throw NotFoundException when product not found', async () => {
      const productId = 'non-existent-id';
      mockRepository.findOne.mockResolvedValue(null);

      await expect(service.findOne(productId)).rejects.toThrow(NotFoundException);
    });
  });
});
```

---

### STEP 9: Configuración del Proyecto

**Archivo**: `src/main.ts`

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global prefix
  app.setGlobalPrefix('api/v1');

  // Validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // CORS
  app.enableCors();

  // Swagger documentation
  const config = new DocumentBuilder()
    .setTitle('Products API')
    .setDescription('RESTful API for product management')
    .setVersion('1.0')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);

  await app.listen(3000);
  console.log(`Application is running on: http://localhost:3000/api/v1`);
  console.log(`Swagger docs available at: http://localhost:3000/api/docs`);
}
bootstrap();
```

---

## 📤 Output Generado

### Archivos Creados

```
backend/                          # NestJS 10 + TypeScript project
├── src/                          # 50+ archivos TypeScript
│   ├── modules/                  # Feature modules
│   │   ├── products/             # Product module completo
│   │   ├── categories/           # Category module
│   │   └── auth/                 # Auth module (JWT)
│   ├── common/                   # Shared code
│   ├── config/                   # Configuration
│   ├── app.module.ts
│   └── main.ts
├── test/                         # E2E tests
├── package.json                  # Dependencies
├── nest-cli.json                 # NestJS CLI config
└── README.md                     # Backend documentation
```

---

## ✅ Definition of Done

Un backend NestJS está **DONE** cuando:

- [x] Proyecto NestJS 10 + TypeScript creado
- [x] Dependencies instaladas (TypeORM, class-validator, Swagger, JWT)
- [x] Entities TypeORM con relaciones definidas
- [x] DTOs con class-validator validations
- [x] Services con business logic y TypeORM repositories
- [x] Controllers RESTful con Swagger decorators
- [x] Modules configurados e importados
- [x] Auth module con JWT strategy y guards
- [x] Global exception filter
- [x] Global validation pipe
- [x] Swagger documentation generada
- [x] TypeORM configuration con PostgreSQL
- [x] Environment configuration (ConfigModule)
- [x] Unit tests (≥80% coverage)
- [x] README.md con instrucciones de setup

---

**Versión**: 1.0.0  
**Autor**: AI Agent Skills Team  
**Última actualización**: 22 de mayo de 2026  
**Licencia**: MIT
