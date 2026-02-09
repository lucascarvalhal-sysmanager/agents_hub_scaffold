import logging
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError

logger = logging.getLogger(__name__)

@dataclass
class FinopsReport:
    """Data Transfer Object for FinOps reporting."""
    user_id: Optional[str] = None
    agent_base_url: Optional[str] = None
    agent_app_name: Optional[str] = None
    session_id: Optional[str] = None
    invocation_id: Optional[str] = None
    user_prompt: str = "N/A"
    agent_response: str = "N/A"
    thoughts_token_count: int = 0
    prompt_token_count: int = 0
    candidates_token_count: int = 0
    cached_content_token_count: int = 0
    total_token_count: int = 0
    interaction_timestamp: Optional[str] = None
    execution_time_ms: float = 0.0
    model_name: str = "unknown_model"
    interaction_kind: str = "agent"

class PersistenceProvider(ABC):
    """Abstract Strategy for data persistence."""
    
    @abstractmethod
    def persist(self, report: FinopsReport) -> None:
        """Persist the report object to the storage medium."""
        pass

    @abstractmethod
    def persist_batch(self, reports: List[FinopsReport]) -> None:
        """Persist a batch of report objects to the storage medium."""
        pass

class BigQueryProvider(PersistenceProvider):
    """Concrete Strategy for Google BigQuery persistence."""
    
    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        
        # Initialize client
        self.client = bigquery.Client(project=project_id)
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        logger.info(f"[FinOps] Initialized BigQuery Provider: {self.table_ref}")

    def persist(self, report: FinopsReport) -> None:
        self.persist_batch([report])

    def persist_batch(self, reports: List[FinopsReport]) -> None:
        if not reports:
            return

        try:
            # Convert Dataclasses to Dictionaries if needed
            rows = []
            for report in reports:
                if isinstance(report, FinopsReport):
                    rows.append(asdict(report))
                elif isinstance(report, dict):
                    rows.append(report)
                else:
                    logger.warning(f"[FinOps] Skipping invalid report format: {type(report)}")

            if not rows:
                return
            
            # BigQuery insert_rows_json expects a list of rows
            errors = self.client.insert_rows_json(self.table_ref, rows)
            logger.info(f"[FinOps] Data inserted into table '{self.table_ref}'")
            
            if errors:
                # errors is a list of mappings with 'index', 'errors' keys
                logger.error(f"[FinOps] BigQuery batch insert failed with errors: {errors}")
            else:
                logger.debug(f"[FinOps] Successfully persisted {len(reports)} reports to BigQuery.")
                
        except GoogleAPICallError as e:
            logger.error(f"[FinOps] BigQuery API call failed: {e}")
        except Exception as e:
            logger.error(f"[FinOps] Unexpected error during BigQuery persistence: {e}")

class FinopsPersistenceService:
    """
    Service context that delegates persistence to the injected provider.
    """
    
    def __init__(self, provider: PersistenceProvider):
        self.provider = provider

    def save_report(self, report: FinopsReport) -> None:
        self.provider.persist(report)

    def save_reports_batch(self, reports: List[FinopsReport]) -> None:
        self.provider.persist_batch(reports)

class PersistenceFactory:
    """Factory to create persistence services based on configuration."""
    
    @staticmethod
    def create_service() -> Optional[FinopsPersistenceService]:
        """Creates a service instance based on environment variables."""
        from typing import Optional 
        
        provider_type = os.getenv("FINOPS_PROVIDER_TYPE", "").lower()
        provider: Optional[PersistenceProvider] = None

        if provider_type == "bigquery":
            project = os.getenv("FINOPS_BQ_PROJECT_ID")
            dataset = os.getenv("FINOPS_BQ_DATASET_ID")
            table = os.getenv("FINOPS_BQ_TABLE_ID")
            
            if project and dataset and table:
                try:
                    provider = BigQueryProvider(project, dataset, table)
                except Exception as e:
                    logger.error(f"[FinOps] Failed to create BigQuery provider: {e}")
            else:
                logger.warning("[FinOps] BigQuery provider requested but configuration missing.")
        
        if provider:
            return FinopsPersistenceService(provider)
        
        return None
