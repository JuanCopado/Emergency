# Clinical image intake and attachment recovery

Use this before interpreting an uploaded clinical image.

## Resolve the actual attachment

1. Prefer the current turn's attachment and its explicitly supplied workspace path.
2. If the first local read reports that the file is absent but the turn also says a
   scratch copy was materialized, retry the exact materialized path once.
3. If the interface supplies several images, enumerate them in message order and
   preserve that order. Do not assume they are the same patient, side, date or study.
4. Never substitute a similarly named historical file or search unrelated folders.
5. After one failed retry, state that pixels were not accessible and request a new
   attachment/export. Do not generate visual findings from the filename or history.
6. When a scratch copy is explicitly provided, use it directly; do not make an
   unnecessary external or Library read merely to inspect it.

## Privacy

- Prefer de-identified files. Do not reproduce visible identifiers in the answer.
- Do not send clinical images or identifiers to web search or third-party services.
- Do not store a patient image in a validation set without authorization,
  de-identification and an independently established reference diagnosis.

## Intake record

Record what is known without inventing normal values:

- accessible pixels: yes/no;
- source: original export, screenshot, photograph of screen, PDF page or unknown;
- modality and body region;
- laterality marker and whether laterality was provided clinically;
- number of supplied images, views/slices/frames and projection/sequence if known;
- technical quality and artifacts;
- age, symptoms, onset/mechanism, relevant examination and vitals;
- the focused clinical question.

Missing metadata limits confidence but does not prevent describing an obvious
visible finding. It does prevent unsupported measurements, whole-study exclusion,
laterality assignment or management decisions that require the missing context.

