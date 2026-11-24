import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';
import NoEntryOverride from '../clinical-note/noEntryOverride';

describe('default modality entry override', () => {
  it('renders nothing: without an explicit non-production opt-in the product entry is the only one', () => {
    const { container } = render(<NoEntryOverride busy={false} language="es" ui={key => key} onConfirm={() => undefined} />);
    expect(container).toBeEmptyDOMElement();
  });
});
