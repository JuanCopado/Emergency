import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <div className="card mx-auto max-w-lg p-8 text-center">
      <h1 className="text-2xl font-bold">{t('notFound.title')}</h1>
      <p className="mt-2 text-muted">{t('notFound.body')}</p>
      <Link to="/" className="btn-primary mt-5">
        {t('nav.home')}
      </Link>
    </div>
  );
}
