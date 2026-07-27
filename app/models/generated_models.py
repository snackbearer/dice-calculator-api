from typing import Optional
import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class MaterialType(Base):
    __tablename__ = 'material_type'
    __table_args__ = (
        PrimaryKeyConstraint('material_type_id', name='material_type_pkey'),
        UniqueConstraint('code', name='uq_material_type_code')
    )

    material_type_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(String(200))

    material_stock: Mapped[list['MaterialStock']] = relationship('MaterialStock', back_populates='material_type')
    production_method_material: Mapped[list['ProductionMethodMaterial']] = relationship('ProductionMethodMaterial', back_populates='material_type')


class ProductionMethod(Base):
    __tablename__ = 'production_method'
    __table_args__ = (
        PrimaryKeyConstraint('production_method_id', name='production_method_pkey'),
        UniqueConstraint('code', name='uq_production_method_code')
    )

    production_method_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(String(200))

    production_method_material: Mapped[list['ProductionMethodMaterial']] = relationship('ProductionMethodMaterial', back_populates='production_method')
    dice_job: Mapped[list['DiceJob']] = relationship('DiceJob', back_populates='production_method')


class MaterialStock(Base):
    __tablename__ = 'material_stock'
    __table_args__ = (
        CheckConstraint('quantity_in_stock >= 0', name='chk_material_stock_quantity'),
        ForeignKeyConstraint(['material_type_id'], ['material_type.material_type_id'], name='fk_material_stock_material_type'),
        PrimaryKeyConstraint('material_stock_id', name='material_stock_pkey'),
        Index('ix_material_stock_material_type', 'material_type_id')
    )

    material_stock_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    colour_name: Mapped[str] = mapped_column(String(100), nullable=False)
    material_type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    material_type: Mapped['MaterialType'] = relationship('MaterialType', back_populates='material_stock')
    dice_job: Mapped[list['DiceJob']] = relationship('DiceJob', back_populates='primary_material_stock')
    dice_job_colour: Mapped[list['DiceJobColour']] = relationship('DiceJobColour', back_populates='material_stock')


class ProductionMethodMaterial(Base):
    __tablename__ = 'production_method_material'
    __table_args__ = (
        ForeignKeyConstraint(['material_type_id'], ['material_type.material_type_id'], ondelete='CASCADE', name='fk_method_material_type'),
        ForeignKeyConstraint(['production_method_id'], ['production_method.production_method_id'], ondelete='CASCADE', name='fk_method_material_method'),
        PrimaryKeyConstraint('production_method_id', 'material_type_id', name='production_method_material_pkey'),
        Index('ix_method_material_type', 'material_type_id')
    )

    production_method_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    material_type_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    material_type: Mapped['MaterialType'] = relationship('MaterialType', back_populates='production_method_material')
    production_method: Mapped['ProductionMethod'] = relationship('ProductionMethod', back_populates='production_method_material')


class DiceJob(Base):
    __tablename__ = 'dice_job'
    __table_args__ = (
        CheckConstraint('colour_count > 0', name='chk_colour_count'),
        ForeignKeyConstraint(['primary_material_stock_id'], ['material_stock.material_stock_id'], name='fk_dice_job_primary_material'),
        ForeignKeyConstraint(['production_method_id'], ['production_method.production_method_id'], name='fk_dice_job_method'),
        PrimaryKeyConstraint('dice_job_id', name='dice_job_pkey'),
        Index('ix_dice_job_material', 'primary_material_stock_id'),
        Index('ix_dice_job_method', 'production_method_id')
    )

    dice_job_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    colour_count: Mapped[int] = mapped_column(Integer, nullable=False)
    production_method_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    primary_material_stock_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    primary_material_stock: Mapped[Optional['MaterialStock']] = relationship('MaterialStock', back_populates='dice_job')
    production_method: Mapped['ProductionMethod'] = relationship('ProductionMethod', back_populates='dice_job')
    dice_job_colour: Mapped[list['DiceJobColour']] = relationship('DiceJobColour', back_populates='dice_job')


class DiceJobColour(Base):
    __tablename__ = 'dice_job_colour'
    __table_args__ = (
        ForeignKeyConstraint(['dice_job_id'], ['dice_job.dice_job_id'], ondelete='CASCADE', name='fk_job_colour_job'),
        ForeignKeyConstraint(['material_stock_id'], ['material_stock.material_stock_id'], name='fk_job_colour_material'),
        PrimaryKeyConstraint('dice_job_colour_id', name='dice_job_colour_pkey'),
        UniqueConstraint('dice_job_id', 'material_stock_id', name='uq_job_colour'),
        Index('ix_job_colour_job', 'dice_job_id'),
        Index('ix_job_colour_material', 'material_stock_id')
    )

    dice_job_colour_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    dice_job_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    material_stock_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    colour_order: Mapped[Optional[int]] = mapped_column(SmallInteger)

    dice_job: Mapped['DiceJob'] = relationship('DiceJob', back_populates='dice_job_colour')
    material_stock: Mapped['MaterialStock'] = relationship('MaterialStock', back_populates='dice_job_colour')
