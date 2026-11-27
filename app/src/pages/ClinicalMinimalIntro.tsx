import { Fragment } from 'react';
import { useTranslation } from 'react-i18next';
import copy from './clinical-minimal-copy.json';

/** Approved illustration and introduction; the real home tools remain separate. */
export function ClinicalMinimalIntro() {
  const { i18n } = useTranslation();
  const language = i18n.resolvedLanguage ?? i18n.language;
  const text = copy[language as keyof typeof copy] ?? copy.es;
  return (
    <div className="clinical-minimal-intro">
      <div>
        <p className="clinical-minimal-eyebrow">{text.eyebrow}</p>
        <h1 id="home-title">
          {text.title.split('<br>').map((line, index) => (
            <Fragment key={line}>{index > 0 && <br />}{line}</Fragment>
          ))}
        </h1>
        <p className="clinical-minimal-lede">{text.lede}</p>
      </div>
      <figure className="clinical-minimal-scene">
        <p className="clinical-minimal-scene-caption">{text.scene}</p>
        <img
          src={`${import.meta.env.BASE_URL}design/clinical-minimal-physician.svg`}
          width="540"
          height="470"
          alt={text.doctorDesc}
          title={text.doctorTitle}
          decoding="async"
        />
        <figcaption>{text.human}</figcaption>
      </figure>
    </div>
  );
}
