"""Pacchetto dei modelli core tenant-aware."""

from app.models.core.anagrafica import Anagrafica
from app.models.core.anagrafica_indirizzo import AnagraficaIndirizzo
from app.models.core.articolo import Articolo
from app.models.core.bolla import Bolla
from app.models.core.bolla_riga import BollaRiga
from app.models.core.bom import Bom
from app.models.core.categoria_articolo import CategoriaArticolo
from app.models.core.finance_cost_entry import FinanceCostEntry
from app.models.core.notification import Notification
from app.models.core.tenant_company_settings import TenantCompanySettings
from app.models.core.tenant_document_sequence import TenantDocumentSequence
from app.models.core.tenant_smtp_settings import TenantSmtpSettings

__all__ = [
    "Anagrafica",
    "AnagraficaIndirizzo",
    "Articolo",
    "Bolla",
    "BollaRiga",
    "Bom",
    "CategoriaArticolo",
    "FinanceCostEntry",
    "Notification",
    "TenantCompanySettings",
    "TenantDocumentSequence",
    "TenantSmtpSettings",
]
