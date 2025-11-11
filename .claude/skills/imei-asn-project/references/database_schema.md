# Database Schema Documentation

Complete PostgreSQL schema for the IMEI-ASN-Match application.

## Tables

### OrderReconciliation

Primary table for tracking order processing and file uploads.

```python
class OrderReconciliation(Base):
    __tablename__ = 'order_reconciliation'

    id = Column(Integer, primary_key=True)
    invoice = Column(String, unique=True, nullable=False, index=True)

    # ASN File fields
    asn_uploaded = Column(Boolean, default=False)
    asn_filename = Column(String)
    asn_file_data = Column(LargeBinary)  # Binary BLOB storage
    asn_upload_date = Column(DateTime)

    # IMEI/Serial File fields
    imei_serial_uploaded = Column(Boolean, default=False)
    imei_serial_filename = Column(String)
    imei_serial_file_data = Column(LargeBinary)  # Binary BLOB storage
    imei_serial_upload_date = Column(DateTime)
    imei_serial_count = Column(Integer)

    # Metadata
    notes = Column(Text)
    error_log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Usage:**
- Track which invoices have ASN files uploaded
- Store original file data for download later
- Count IMEI/Serial entries for reconciliation
- Maintain notes and error logs per invoice

**Migrations:**
Recent schema additions handled in `_run_migrations()`:
- Added `imei_serial_count` column
- Added file storage columns (asn_file_data, imei_serial_file_data)

### ArchivedOrder

Stores completed/archived orders for historical record.

```python
class ArchivedOrder(Base):
    __tablename__ = 'archived_orders'

    id = Column(Integer, primary_key=True)
    invoice = Column(String, unique=True, nullable=False, index=True)
    order_data = Column(Text)  # JSON string of order details
    total_qty = Column(Integer)
    unique_models = Column(Integer)
    notes = Column(Text)
    archived_at = Column(DateTime, default=datetime.utcnow)
    original_created_at = Column(DateTime)
```

**Usage:**
- Move completed orders from OrderReconciliation
- Maintain historical record
- Support restore functionality
- Enable cleanup of active orders

**Important:** When archiving, ensure numpy types are converted to Python int:
```python
total_qty_int = int(total_qty) if total_qty is not None else None
unique_models_int = int(unique_models) if unique_models is not None else None
```

### OrderLineItem

Individual line items for each order (future enhancement).

```python
class OrderLineItem(Base):
    __tablename__ = 'order_line_items'

    id = Column(Integer, primary_key=True)
    invoice = Column(String, ForeignKey('order_reconciliation.invoice'), nullable=False)
    model = Column(String)
    capacity = Column(String)
    grade = Column(String)
    qty = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Usage:**
- Store granular line item data
- Enable advanced querying and reporting
- Support detailed reconciliation

### SupplierProfile

Configuration for different suppliers (future enhancement).

```python
class SupplierProfile(Base):
    __tablename__ = 'supplier_profiles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Usage:**
- Store supplier-specific configurations
- Enable per-supplier data handling
- Support multiple data source formats

### ColumnMapping

Maps source columns to standard fields (future enhancement).

```python
class ColumnMapping(Base):
    __tablename__ = 'column_mappings'

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('supplier_profiles.id'), nullable=False)
    source_column = Column(String, nullable=False)
    target_field = Column(String, nullable=False)
    transformation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Usage:**
- Map different supplier column formats
- Support data transformations
- Enable flexible data import

## Common Queries

### Get all orders with ASN uploaded
```python
session.query(OrderReconciliation).filter_by(asn_uploaded=True).all()
```

### Get order statistics
```python
def get_order_statistics():
    total_orders = session.query(OrderReconciliation).count()
    asn_uploads = session.query(OrderReconciliation).filter_by(asn_uploaded=True).count()
    imei_uploads = session.query(OrderReconciliation).filter_by(imei_serial_uploaded=True).count()
    return {'total': total_orders, 'asn': asn_uploads, 'imei': imei_uploads}
```

### Archive an order
```python
def archive_order(invoice, order_data, total_qty, unique_models, notes=None):
    # Convert numpy types to Python native
    total_qty_int = int(total_qty) if total_qty is not None else None
    unique_models_int = int(unique_models) if unique_models is not None else None

    # Create archived record
    archived = ArchivedOrder(
        invoice=invoice,
        order_data=json.dumps(order_data),
        total_qty=total_qty_int,
        unique_models=unique_models_int,
        notes=notes
    )
    session.add(archived)
    session.flush()  # Important: flush before delete to avoid autoflush issues

    # Delete from active orders
    session.query(OrderReconciliation).filter_by(invoice=invoice).delete()
    session.commit()
```

## Migration Patterns

Migrations run automatically on application startup via `_run_migrations()`:

```python
def _run_migrations(engine):
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='order_reconciliation'
            AND column_name='imei_serial_count'
        """))

        if not result.fetchone():
            # Add new column
            conn.execute(text("""
                ALTER TABLE order_reconciliation
                ADD COLUMN imei_serial_count INTEGER
            """))
            conn.commit()
```

## Best Practices

1. **Type Conversion**: Always convert numpy/pandas types to Python natives before database insert
2. **File Storage**: Store files as binary blobs, not file paths
3. **Timestamps**: Use UTC timezone for all datetime fields
4. **Indexing**: Invoice columns are indexed for fast lookups
5. **Migrations**: Test migrations locally before Railway deployment
6. **Session Management**: Use context managers or explicit close() for sessions
