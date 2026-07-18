# Database Review

Database schema, index, and query optimization review.

## Checklist

### Schema Design
- Appropriate normalization level
- Primary key and foreign key definitions
- Data type selection
- Default values and constraints

### Indexing
- Appropriate indexes for common queries
- Avoid excessive indexes
- Composite index ordering
- Index selectivity

### Query Optimization
- Avoid SELECT *
- Proper use of JOIN
- Pagination optimization (OFFSET vs Cursor)
- Batch operations instead of loops

### Migration
- Migration scripts are reversible
- Large table migration strategy
- Data consistency
