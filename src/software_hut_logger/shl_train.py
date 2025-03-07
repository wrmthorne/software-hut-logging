from datasets import load_dataset
import evaluate
import torch
import psutil
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    HfArgumentParser,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)

from software_hut_logger import SoftwareHutLogger, ScriptArguments


DATASETS_NUM_PROC = psutil.cpu_count(logical=False)


def compute_metrics_factory(tokenizer):
    metrics = evaluate.combine(["sacrebleu", "rouge", "meteor"], force_prefix=True)
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        detokenized_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        detokenized_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        return metrics.compute(predictions=detokenized_preds, references=detokenized_labels)
    return compute_metrics


def tokenize(batch, tokenizer, max_length=512):
    task_prefix = "Translate English to German: "
    # Tokenize inputs
    model_inputs = tokenizer(
        [task_prefix + example for example in batch["text"]],
        max_length=max_length,
        padding=False,
        truncation=True,
        return_attention_mask=True,
    )
    
    # Tokenize labels separately
    labels = tokenizer(
        batch["labels"],
        max_length=max_length,
        padding=False,
        truncation=True,
    )
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def prepare_wmt14_en_de_datasets(tokenizer, num_train_samples=-1, num_test_samples=-1, seed=42, max_length=512):
    dataset = load_dataset("wmt14", "de-en")
    
    dataset['train'] = dataset['train'].shuffle(seed=seed).select(range(num_train_samples)) \
        if num_train_samples != -1 else dataset['train']
    dataset['validation'] = dataset['validation'].shuffle(seed=seed).select(range(num_test_samples)) \
        if num_test_samples != -1 else dataset['validation']
    
    dataset = dataset.map(
        lambda x: {"text": x["translation"]["en"], "labels": x["translation"]["de"]},
        desc="Converting to text-labels format",
        num_proc=DATASETS_NUM_PROC,
    ).remove_columns(["translation"])
    
    print("Initial dataset:", dataset)
    print("Sample before tokenization:", dataset["train"][0])
    
    dataset = dataset.map(
        lambda batch: tokenize(
            batch,
            tokenizer,
            max_length
        ),
        batched=True,
        batch_size=200,
        num_proc=DATASETS_NUM_PROC,
    )
    return dataset


def parse_train_args():
    parser = HfArgumentParser((ScriptArguments, Seq2SeqTrainingArguments))
    script_args, training_args = parser.parse_args_into_dataclasses()
    return script_args, training_args


def main():
    script_args, training_args = parse_train_args()

    model_kwargs = dict(
        torch_dtype=torch.float32,
        use_cache=False if training_args.gradient_checkpointing else True,
        device_map=None,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        script_args.model_name_or_path, 
        **model_kwargs
    )
    tokenizer = AutoTokenizer.from_pretrained(
        script_args.model_name_or_path, 
        use_fast=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Prepare wmt14 en-de translation benchmark dataset
    dataset = prepare_wmt14_en_de_datasets(
        tokenizer,
        script_args.num_train_samples,
        script_args.num_test_samples,
        training_args.seed,
        script_args.max_length,
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding="longest",
        pad_to_multiple_of=8,
        label_pad_token_id=tokenizer.pad_token_id,
    )

    compute_metrics = compute_metrics_factory(tokenizer)
    sh_logger = SoftwareHutLogger()

    trainer = Seq2SeqTrainer(
        model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"] if training_args.eval_strategy != "no" else None,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
        data_collator=data_collator,
        callbacks=[sh_logger],
    )
    trainer.train()

    # Save and push to hub
    trainer.save_model(training_args.output_dir)
    if training_args.push_to_hub:
        trainer.push_to_hub(dataset_name=script_args.dataset_name)


if __name__ == "__main__":
    main()