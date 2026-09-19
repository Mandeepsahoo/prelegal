"use client";

import { NdaFormData, PartyInfo } from "@/lib/nda/types";

interface NdaFormProps {
  value: NdaFormData;
  onChange: (next: NdaFormData) => void;
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100";

function PartyFields({
  legend,
  value,
  onChange,
}: {
  legend: string;
  value: PartyInfo;
  onChange: (next: PartyInfo) => void;
}) {
  return (
    <fieldset className="flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
      <legend className="px-1 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
        {legend}
      </legend>
      <Field label="Print Name">
        <input
          className={inputClass}
          value={value.name}
          onChange={(e) => onChange({ ...value, name: e.target.value })}
          placeholder="Jane Doe"
        />
      </Field>
      <Field label="Title">
        <input
          className={inputClass}
          value={value.title}
          onChange={(e) => onChange({ ...value, title: e.target.value })}
          placeholder="Chief Executive Officer"
        />
      </Field>
      <Field label="Company">
        <input
          className={inputClass}
          value={value.company}
          onChange={(e) => onChange({ ...value, company: e.target.value })}
          placeholder="Acme, Inc."
        />
      </Field>
      <Field label="Notice Address">
        <input
          className={inputClass}
          value={value.noticeAddress}
          onChange={(e) => onChange({ ...value, noticeAddress: e.target.value })}
          placeholder="legal@acme.com"
        />
      </Field>
    </fieldset>
  );
}

export function NdaForm({ value, onChange }: NdaFormProps) {
  const set = <K extends keyof NdaFormData>(key: K, fieldValue: NdaFormData[K]) =>
    onChange({ ...value, [key]: fieldValue });

  return (
    <form className="flex flex-col gap-6" onSubmit={(e) => e.preventDefault()}>
      <fieldset className="flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
        <legend className="px-1 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          Agreement Details
        </legend>
        <Field label="Purpose">
          <textarea
            className={inputClass}
            rows={2}
            value={value.purpose}
            onChange={(e) => set("purpose", e.target.value)}
          />
        </Field>
        <Field label="Effective Date">
          <input
            type="date"
            className={inputClass}
            value={value.effectiveDate}
            onChange={(e) => set("effectiveDate", e.target.value)}
          />
        </Field>

        <div className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-zinc-700 dark:text-zinc-300">MNDA Term</span>
          <div className="flex items-center gap-2">
            <input
              type="radio"
              id="term-fixed"
              checked={value.termType === "fixed"}
              onChange={() => set("termType", "fixed")}
            />
            <label htmlFor="term-fixed">Expires</label>
            <input
              type="number"
              min={1}
              className={`${inputClass} w-20`}
              value={value.termYears}
              disabled={value.termType !== "fixed"}
              onChange={(e) => set("termYears", Number(e.target.value) || 1)}
            />
            <span>year(s) from Effective Date</span>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="radio"
              id="term-until-terminated"
              checked={value.termType === "until-terminated"}
              onChange={() => set("termType", "until-terminated")}
            />
            <label htmlFor="term-until-terminated">
              Continues until terminated in accordance with the terms of the MNDA
            </label>
          </div>
        </div>

        <div className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            Term of Confidentiality
          </span>
          <div className="flex items-center gap-2">
            <input
              type="radio"
              id="confidentiality-fixed"
              checked={value.confidentialityType === "fixed"}
              onChange={() => set("confidentialityType", "fixed")}
            />
            <input
              type="number"
              min={1}
              className={`${inputClass} w-20`}
              value={value.confidentialityYears}
              disabled={value.confidentialityType !== "fixed"}
              onChange={(e) => set("confidentialityYears", Number(e.target.value) || 1)}
            />
            <label htmlFor="confidentiality-fixed">year(s) from Effective Date</label>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="radio"
              id="confidentiality-perpetuity"
              checked={value.confidentialityType === "perpetuity"}
              onChange={() => set("confidentialityType", "perpetuity")}
            />
            <label htmlFor="confidentiality-perpetuity">In perpetuity</label>
          </div>
        </div>

        <Field label="Governing Law (state)">
          <input
            className={inputClass}
            value={value.governingLaw}
            onChange={(e) => set("governingLaw", e.target.value)}
            placeholder="Delaware"
          />
        </Field>
        <Field label="Jurisdiction">
          <input
            className={inputClass}
            value={value.jurisdiction}
            onChange={(e) => set("jurisdiction", e.target.value)}
            placeholder="courts located in New Castle, DE"
          />
        </Field>
        <Field label="MNDA Modifications (optional)">
          <textarea
            className={inputClass}
            rows={2}
            value={value.modifications}
            onChange={(e) => set("modifications", e.target.value)}
          />
        </Field>
      </fieldset>

      <PartyFields
        legend="Party 1"
        value={value.partyA}
        onChange={(next) => set("partyA", next)}
      />
      <PartyFields
        legend="Party 2"
        value={value.partyB}
        onChange={(next) => set("partyB", next)}
      />
    </form>
  );
}
