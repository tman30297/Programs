#!/usr/bin/env python3
"""
Data Processing Pipeline Template
ETL pipeline with extraction, transformation, and loading stages.
"""

import pandas as pd
import logging
import json
from pathlib import Path
from typing import Any, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    input_path: str
    output_path: str
    log_path: str = "pipeline.log"


class DataPipeline:
    """ETL Pipeline with configurable stages."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.stages: List[Callable[[pd.DataFrame], pd.DataFrame]] = []
        self.logger = logging.getLogger(__name__)
    
    def add_stage(self, name: str, func: Callable[[pd.DataFrame], pd.DataFrame]):
        """Add a transformation stage."""
        self.stages.append(func)
        self.logger.info(f"Added stage: {name}")
    
    def extract(self, path: str) -> pd.DataFrame:
        """Extract data from source."""
        self.logger.info(f"Extracting from {path}")
        p = Path(path)
        
        if p.suffix == ".csv":
            return pd.read_csv(path)
        elif p.suffix == ".json":
            return pd.read_json(path)
        elif p.suffix == ".xlsx":
            return pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format: {p.suffix}")
    
    def load(self, df: pd.DataFrame, path: str):
        """Load data to destination."""
        self.logger.info(f"Loading to {path}")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        if p.suffix == ".csv":
            df.to_csv(path, index=False)
        elif p.suffix == ".json":
            df.to_json(path, orient="records", indent=2)
        elif p.suffix == ".xlsx":
            df.to_excel(path, index=False)
    
    def run(self) -> Dict[str, Any]:
        """Execute the pipeline."""
        start_time = datetime.now()
        report = {"start_time": start_time.isoformat(), "stages": []}
        
        try:
            # Extract
            df = self.extract(self.config.input_path)
            report["input_rows"] = len(df)
            self.logger.info(f"Extracted {len(df)} rows")
            
            # Transform stages
            for i, stage in enumerate(self.stages):
                stage_name = stage.__name__
                self.logger.info(f"Running stage {i+1}: {stage_name}")
                df = stage(df)
                report["stages"].append({"stage": stage_name, "rows": len(df)})
            
            # Load
            self.load(df, self.config.output_path)
            report["output_rows"] = len(df)
            report["status"] = "success"
            
        except Exception as e:
            report["status"] = "failed"
            report["error"] = str(e)
            self.logger.error(f"Pipeline failed: {e}")
        
        report["end_time"] = datetime.now().isoformat()
        
        # Save report
        Path(self.config.log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config.log_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report


def filter_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filter rows based on condition."""
    return df[df["value"] > 0]

def add_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed column."""
    df["processed_at"] = datetime.now()
    return df


if __name__ == "__main__":
    config = PipelineConfig(
        input_path="data/input.csv",
        output_path="data/output.csv",
        log_path="logs/pipeline_report.json"
    )
    
    pipeline = DataPipeline(config)
    pipeline.add_stage("filter", filter_rows)
    pipeline.add_stage("add_column", add_column)
    
    result = pipeline.run()
    logger.info(f"Pipeline result: {result['status']}")