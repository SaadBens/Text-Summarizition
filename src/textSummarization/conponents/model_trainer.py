from transformers import TrainingArguments, Trainer
from transformers import DataCollatorForSeq2Seq
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from datasets import load_dataset, load_from_disk
from textSummarization.entity import ModelTrainerConfig
import torch
import os


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config


    
    def train(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokenizer = AutoTokenizer.from_pretrained(self.config.model_ckpt)
        model_flan_t5 = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_ckpt).to(device)
        seq2seq_data_collator = DataCollatorForSeq2Seq(tokenizer, model=model_flan_t5)
        
        #loading data 
        dataset_pt = load_from_disk(self.config.data_path)

        trainer_args = TrainingArguments(
            output_dir=self.config.root_dir, 
            num_train_epochs=self.config.num_train_epochs, 
            per_device_train_batch_size=self.config.per_device_train_batch_size, 
            per_device_eval_batch_size=self.config.per_device_train_batch_size,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps
            
        ) 

        trainer = Trainer(
            model=model_flan_t5, 
            args=trainer_args,
            tokenizer=tokenizer, 
            data_collator=seq2seq_data_collator,
            train_dataset=dataset_pt["train"], 
            eval_dataset=dataset_pt["validation"])
        
        trainer.train()

        ## Save model
        model_flan_t5.save_pretrained(os.path.join(self.config.root_dir,"flant5-dialogsum-model"))
        ## Save tokenizer
        tokenizer.save_pretrained(os.path.join(self.config.root_dir,"tokenizer"))

