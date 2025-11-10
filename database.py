import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

Base = declarative_base()

class OrderReconciliation(Base):
    __tablename__ = 'order_reconciliation'

    id = Column(Integer, primary_key=True)
    invoice = Column(String, unique=True, nullable=False, index=True)
    reconciled = Column(Boolean, default=False)
    reconciled_date = Column(DateTime, nullable=True)
    asn_uploaded = Column(Boolean, default=False)
    asn_filename = Column(String, nullable=True)
    asn_file_data = Column(LargeBinary, nullable=True)
    asn_upload_date = Column(DateTime, nullable=True)
    imei_serial_uploaded = Column(Boolean, default=False)
    imei_serial_filename = Column(String, nullable=True)
    imei_serial_file_data = Column(LargeBinary, nullable=True)
    imei_serial_upload_date = Column(DateTime, nullable=True)
    imei_serial_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderLineItem(Base):
    __tablename__ = 'order_line_items'
    
    id = Column(Integer, primary_key=True)
    invoice = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    capacity = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    expected_qty = Column(Integer, nullable=False)
    received_qty = Column(Integer, nullable=True)
    variance = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SupplierProfile(Base):
    __tablename__ = 'supplier_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ColumnMapping(Base):
    __tablename__ = 'column_mappings'

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('supplier_profiles.id'), nullable=False, index=True)
    source_column = Column(String, nullable=False)
    target_field = Column(String, nullable=False)
    transformation = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ArchivedOrder(Base):
    __tablename__ = 'archived_orders'

    id = Column(Integer, primary_key=True)
    invoice = Column(String, nullable=False, index=True)
    # Order details from Google Sheets
    order_data = Column(Text, nullable=True)  # JSON string of order line items
    total_qty = Column(Integer, nullable=True)
    unique_models = Column(Integer, nullable=True)
    # Files
    asn_filename = Column(String, nullable=True)
    asn_file_data = Column(LargeBinary, nullable=True)
    imei_serial_filename = Column(String, nullable=True)
    imei_serial_file_data = Column(LargeBinary, nullable=True)
    # Metadata
    notes = Column(Text, nullable=True)
    archived_date = Column(DateTime, default=datetime.utcnow)
    archived_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

@st.cache_resource
def get_database_engine():
    """Create and cache the database engine"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return None
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def init_database():
    """Initialize the database tables"""
    engine = get_database_engine()
    if engine is None:
        st.warning("⚠️ Database not configured. Reconciliation and notes features will be unavailable.")
        return None
    Base.metadata.create_all(engine)
    
    # Run migrations for existing databases
    _run_migrations(engine)
    
    return engine

def _run_migrations(engine):
    """Run database migrations for schema updates"""
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    
    # Migration: Add asn_file_data column to order_reconciliation table
    if 'order_reconciliation' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('order_reconciliation')]
        
        if 'asn_file_data' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN asn_file_data BYTEA'))
                    conn.commit()
            except Exception as e:
                # Column might already exist or other error
                pass
        
        # Migration: Add error_log column to order_reconciliation table
        if 'error_log' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN error_log TEXT'))
                    conn.commit()
            except Exception as e:
                # Column might already exist or other error
                pass

        # Migration: Add IMEI/SERIAL tracking columns
        if 'imei_serial_uploaded' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN imei_serial_uploaded BOOLEAN DEFAULT FALSE'))
                    conn.commit()
            except Exception:
                pass

        if 'imei_serial_filename' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN imei_serial_filename VARCHAR'))
                    conn.commit()
            except Exception:
                pass

        if 'imei_serial_file_data' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN imei_serial_file_data BYTEA'))
                    conn.commit()
            except Exception:
                pass

        if 'imei_serial_upload_date' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN imei_serial_upload_date TIMESTAMP'))
                    conn.commit()
            except Exception:
                pass

        if 'imei_serial_count' not in columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE order_reconciliation ADD COLUMN imei_serial_count INTEGER'))
                    conn.commit()
            except Exception:
                pass

def get_session():
    """Get a new database session"""
    engine = get_database_engine()
    if engine is None:
        return None
    Session = sessionmaker(bind=engine)
    return Session()

def get_reconciliation_status(invoice):
    """Get reconciliation status for an invoice"""
    session = get_session()
    if session is None:
        return None
    try:
        status = session.query(OrderReconciliation).filter_by(invoice=invoice).first()
        return status
    finally:
        session.close()

def create_or_update_reconciliation(invoice, **kwargs):
    """Create or update reconciliation record"""
    session = get_session()
    if session is None:
        return None
    try:
        status = session.query(OrderReconciliation).filter_by(invoice=invoice).first()
        
        if not status:
            status = OrderReconciliation(invoice=invoice)
            session.add(status)
        
        for key, value in kwargs.items():
            if hasattr(status, key):
                setattr(status, key, value)
        
        status.updated_at = datetime.utcnow()
        session.commit()
        return status
    finally:
        session.close()

def get_all_reconciliations():
    """Get all reconciliation records"""
    session = get_session()
    if session is None:
        return []
    try:
        return session.query(OrderReconciliation).order_by(OrderReconciliation.created_at.desc()).all()
    finally:
        session.close()

def save_order_line_items(invoice, line_items):
    """Save line items for an invoice"""
    session = get_session()
    if session is None:
        return None
    try:
        # Delete existing line items for this invoice
        session.query(OrderLineItem).filter_by(invoice=invoice).delete()
        
        # Add new line items
        for item in line_items:
            line_item = OrderLineItem(
                invoice=invoice,
                model=item.get('MODEL'),
                capacity=item.get('CAPACITY'),
                grade=item.get('GRADE'),
                expected_qty=item.get('EXPECTED_QTY'),
                received_qty=item.get('RECEIVED_QTY'),
                variance=item.get('VARIANCE')
            )
            session.add(line_item)
        
        session.commit()
    finally:
        session.close()

def get_order_line_items(invoice):
    """Get line items for an invoice"""
    session = get_session()
    if session is None:
        return []
    try:
        return session.query(OrderLineItem).filter_by(invoice=invoice).all()
    finally:
        session.close()

def get_all_suppliers():
    """Get all supplier profiles"""
    session = get_session()
    if session is None:
        return []
    try:
        return session.query(SupplierProfile).order_by(SupplierProfile.name).all()
    finally:
        session.close()

def create_or_update_supplier(name, description=None, is_default=False):
    """Create or update supplier profile"""
    session = get_session()
    if session is None:
        return None
    try:
        supplier = session.query(SupplierProfile).filter_by(name=name).first()
        
        if not supplier:
            supplier = SupplierProfile(name=name)
            session.add(supplier)
        
        supplier.description = description
        supplier.is_default = is_default
        supplier.updated_at = datetime.utcnow()
        
        session.commit()
        return supplier
    finally:
        session.close()

def get_column_mappings(supplier_id):
    """Get column mappings for a supplier"""
    session = get_session()
    if session is None:
        return []
    try:
        return session.query(ColumnMapping).filter_by(supplier_id=supplier_id, is_active=True).all()
    finally:
        session.close()

def save_column_mapping(supplier_id, source_column, target_field, transformation=None):
    """Save a column mapping for a supplier"""
    session = get_session()
    if session is None:
        return None
    try:
        # Deactivate existing mapping for this source column
        session.query(ColumnMapping).filter_by(
            supplier_id=supplier_id,
            source_column=source_column
        ).update({'is_active': False})
        
        # Create new mapping
        mapping = ColumnMapping(
            supplier_id=supplier_id,
            source_column=source_column,
            target_field=target_field,
            transformation=transformation,
            is_active=True
        )
        session.add(mapping)
        session.commit()
        return mapping
    finally:
        session.close()

def get_supplier_by_name(name):
    """Get supplier by name"""
    session = get_session()
    if session is None:
        return None
    try:
        return session.query(SupplierProfile).filter_by(name=name).first()
    finally:
        session.close()

def clear_asn_data(invoice):
    """Clear ASN data for a specific invoice"""
    session = get_session()
    if session is None:
        return False
    try:
        recon = session.query(OrderReconciliation).filter_by(invoice=invoice).first()
        if recon:
            recon.asn_uploaded = False
            recon.asn_filename = None
            recon.asn_file_data = None
            recon.asn_upload_date = None
            recon.reconciled = False
            recon.reconciled_date = None
            recon.updated_at = datetime.utcnow()
            session.commit()
            
            # Also clear line items
            session.query(OrderLineItem).filter_by(invoice=invoice).delete()
            session.commit()
            return True
        return False
    finally:
        session.close()

def clear_all_asn_data():
    """Clear ASN data for all invoices that have ASN uploaded"""
    session = get_session()
    if session is None:
        return 0
    try:
        # Get all invoices with ASN data
        asn_invoices = session.query(OrderReconciliation).filter_by(asn_uploaded=True).all()
        count = len(asn_invoices)
        
        if count == 0:
            return 0
        
        # Clear ASN-related fields only for invoices with ASN data
        session.query(OrderReconciliation).filter_by(asn_uploaded=True).update({
            'asn_uploaded': False,
            'asn_filename': None,
            'asn_file_data': None,
            'asn_upload_date': None,
            'reconciled': False,
            'reconciled_date': None,
            'updated_at': datetime.utcnow()
        })
        session.commit()
        
        # Clear line items only for those invoices
        invoice_list = [r.invoice for r in asn_invoices]
        if invoice_list:
            session.query(OrderLineItem).filter(OrderLineItem.invoice.in_(invoice_list)).delete(synchronize_session=False)
            session.commit()
        
        return count
    finally:
        session.close()

def clear_imei_serial_data(invoice):
    """Clear IMEI/SERIAL data for a specific invoice"""
    session = get_session()
    if session is None:
        return False
    try:
        recon = session.query(OrderReconciliation).filter_by(invoice=invoice).first()
        if recon:
            recon.imei_serial_uploaded = False
            recon.imei_serial_filename = None
            recon.imei_serial_file_data = None
            recon.imei_serial_upload_date = None
            recon.imei_serial_count = None
            recon.updated_at = datetime.utcnow()
            session.commit()
            return True
        return False
    finally:
        session.close()

def get_order_statistics():
    """Get statistics about all orders"""
    session = get_session()
    if session is None:
        return {
            'total_orders': 0,
            'with_asn': 0,
            'with_imei': 0,
            'pending': 0
        }
    try:
        all_orders = session.query(OrderReconciliation).all()
        return {
            'total_orders': len(all_orders),
            'with_asn': sum(1 for o in all_orders if o.asn_uploaded),
            'with_imei': sum(1 for o in all_orders if o.imei_serial_uploaded),
            'pending': sum(1 for o in all_orders if not o.asn_uploaded)
        }
    finally:
        session.close()

def archive_order(invoice, order_data, total_qty, unique_models, notes=None):
    """Archive an order with all its data"""
    import json
    session = get_session()
    if session is None:
        return None
    try:
        # Get reconciliation data
        recon = session.query(OrderReconciliation).filter_by(invoice=invoice).first()

        # Convert numpy types to Python native types
        total_qty_int = int(total_qty) if total_qty is not None else None
        unique_models_int = int(unique_models) if unique_models is not None else None

        # Create archived order
        archived = ArchivedOrder(
            invoice=invoice,
            order_data=json.dumps(order_data) if order_data else None,
            total_qty=total_qty_int,
            unique_models=unique_models_int,
            asn_filename=recon.asn_filename if recon else None,
            asn_file_data=recon.asn_file_data if recon else None,
            imei_serial_filename=recon.imei_serial_filename if recon else None,
            imei_serial_file_data=recon.imei_serial_file_data if recon else None,
            notes=notes or (recon.notes if recon else None),
            archived_date=datetime.utcnow()
        )
        session.add(archived)
        session.flush()  # Flush before delete to avoid autoflush issues

        # Delete from reconciliation table
        if recon:
            session.delete(recon)

        # Delete line items
        session.query(OrderLineItem).filter_by(invoice=invoice).delete()

        session.commit()
        return archived
    finally:
        session.close()

def get_all_archived_orders():
    """Get all archived orders"""
    session = get_session()
    if session is None:
        return []
    try:
        return session.query(ArchivedOrder).order_by(ArchivedOrder.archived_date.desc()).all()
    finally:
        session.close()

def get_archived_order(invoice):
    """Get a specific archived order"""
    session = get_session()
    if session is None:
        return None
    try:
        return session.query(ArchivedOrder).filter_by(invoice=invoice).first()
    finally:
        session.close()

def delete_archived_order(invoice):
    """Delete an archived order"""
    session = get_session()
    if session is None:
        return False
    try:
        archived = session.query(ArchivedOrder).filter_by(invoice=invoice).first()
        if archived:
            session.delete(archived)
            session.commit()
            return True
        return False
    finally:
        session.close()
