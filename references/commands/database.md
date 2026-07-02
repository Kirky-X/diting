# Database Review

Database schema, index, and query optimization review.

## Checklist

### Schema Design
- Appropriate level of normalization
- Primary key and foreign key definitions
- Data type selection
- Default values and constraints

### Indexes
- Appropriate indexes for common queries
- Avoid excessive indexes
- Composite index order
- Index selectivity

### Query Optimization
- Avoid SELECT *
- Reasonable use of JOINs
- Pagination optimization (OFFSET vs Cursor)
- Batch operations instead of loops

### Migrations
- Migration scripts are reversible
- Large table migration strategy
- Data consistency
