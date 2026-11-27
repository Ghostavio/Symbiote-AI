# Guia de Testes E2E com Playwright

> Documento de referência para subagentes que implementam testes E2E no projeto.
> Todos os testes E2E devem seguir as convenções descritas aqui.

---

## 1. Padrão: Page Object Model (POM)

Todos os testes devem seguir o padrão **Page Object Model** (https://playwright.dev/docs/pom).

### Princípios

- Cada página/tela tem uma classe Page Object que encapsula **seletores** e **ações**
- Componentes reutilizáveis (carrossel, header, dialogs) têm seus próprios Page Objects
- Os testes (`.spec.ts`) nunca acessam seletores diretamente — sempre via Page Object
- Page Objects nunca fazem assertions — isso é responsabilidade dos testes

### Estrutura de pastas

```
<APP_DIR>/e2e/
  pages/                              # Page Objects
    auth.page.ts                      # Autenticação mock
    <feature>-list.page.ts            # Tela de listagem da feature
    <feature>-details.page.ts         # Tela de detalhes da feature
    components/                       # Page Objects de componentes reutilizáveis
      carousel.component.ts           # Componente de carrossel
      header.component.ts             # Header do app
      qa-helper.component.ts          # QA Helper (se aplicável)
  <feature>/                          # Spec files agrupados por feature
    <feature>-list.spec.ts
    <feature>-details.spec.ts
    <feature>-actions.spec.ts
  fixtures/
    auth.fixture.ts                   # Fixture de autenticação
```

---

## 2. Seletores: sempre `data-testid`

### Regra

Usar `page.getByTestId('...')` como seletor principal. Nunca usar classes CSS (`.minha-classe`), IDs (`#btn-search`) ou seletores de estrutura DOM (`div > span`).

### No componente de UI

Adicionar `data-testid` nos elementos que serão testados (adapte a sintaxe de template ao framework do projeto):

```html
<!-- exemplo: order-card -->
<article data-testid="order-card" class="order-card">
  <h3 data-testid="order-number">...</h3>
  <span data-testid="order-status">...</span>
  <span data-testid="order-total">...</span>
  <button type="button" data-testid="order-view-btn">Visualizar</button>
</article>
```

### No Page Object

```typescript
// pages/<feature>-list.page.ts
import { Page, Locator } from '@playwright/test';

export class FeatureListPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly clearButton: Locator;
  readonly itemCards: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.getByTestId('search-input');
    this.searchButton = page.getByTestId('search-submit-btn');
    this.clearButton = page.getByTestId('search-clear-btn');
    this.itemCards = page.getByTestId('item-card');
    this.emptyState = page.getByTestId('search-empty-state');
  }

  async navigate() {
    await this.page.goto('/<feature-route>');
    await this.page.waitForSelector('form', { timeout: 15000 });
  }

  async searchBy(value: string) {
    await this.searchInput.fill(value);
    await this.searchButton.click();
    await this.itemCards.first().waitFor({ state: 'visible', timeout: 10000 });
  }

  async clearFilters() {
    await this.clearButton.click();
  }

  async getCardCount(): Promise<number> {
    return this.itemCards.count();
  }
}
```

### No teste

```typescript
// <feature>/<feature>-list.spec.ts
import { test, expect } from '../fixtures/auth.fixture';
import { FeatureListPage } from '../pages/<feature>-list.page';

test.describe('Feature List', () => {
  let listPage: FeatureListPage;

  test.beforeEach(async ({ page }) => {
    listPage = new FeatureListPage(page);
    await listPage.navigate();
  });

  test('busca retorna resultado', async () => {
    await listPage.searchBy('valor-conhecido');
    const count = await listPage.getCardCount();
    expect(count).toBeGreaterThan(0);
  });

  test('limpar filtros remove resultados', async () => {
    await listPage.searchBy('valor-conhecido');
    await listPage.clearFilters();
    await expect(listPage.itemCards).toHaveCount(0);
  });
});
```

---

## 3. Page Objects de componentes reutilizáveis

Componentes usados em múltiplas páginas (carrossel, dialogs) devem ter seus próprios Page Objects:

```typescript
// pages/components/carousel.component.ts
import { Page, Locator } from '@playwright/test';

export class CarouselComponent {
  readonly container: Locator;
  readonly items: Locator;
  readonly arrowLeft: Locator;
  readonly arrowRight: Locator;
  readonly footer: Locator;
  readonly pageBoxes: Locator;
  readonly activePageBox: Locator;

  constructor(page: Page, scope?: Locator) {
    const root = scope ?? page;
    this.container = root.getByTestId('carousel');
    this.items = root.getByTestId('carousel-item');
    this.arrowLeft = root.getByTestId('carousel-arrow-left');
    this.arrowRight = root.getByTestId('carousel-arrow-right');
    this.footer = root.getByTestId('carousel-footer');
    this.pageBoxes = root.getByTestId('carousel-page-box');
    this.activePageBox = root.locator('[data-testid="carousel-page-box"][data-active="true"]');
  }

  async getVisibleItemCount(): Promise<number> {
    return this.items.filter({ hasNot: this.items.page().locator('.carousel-item--hidden') }).count();
  }

  async navigateForward() {
    await this.arrowRight.click();
  }

  async navigateBack() {
    await this.arrowLeft.click();
  }
}
```

---

## 4. Convenções de nomeação para `data-testid`

| Padrão                    | Exemplo                                               | Uso                               |
| ------------------------- | ----------------------------------------------------- | --------------------------------- |
| `{componente}-{elemento}` | `order-card`, `carousel-arrow-left`                   | Elementos dentro de um componente |
| `{pagina}-{ação}-btn`     | `search-submit-btn`, `search-clear-btn`               | Botões de ação                    |
| `{pagina}-{campo}-input`  | `search-number-input`, `search-email-input`           | Campos de formulário              |
| `{componente}-{estado}`   | `search-empty-state`, `search-loading`                | Estados da UI                     |
| `{dialog}-{elemento}`     | `cancel-dialog-reason-select`, `export-dialog-year-select` | Elementos dentro de dialogs  |

---

## 5. Autenticação

O mock server do app exige autenticação antes de qualquer teste. Usar o fixture existente:

```typescript
// fixtures/auth.fixture.ts
import { test as base, Page } from '@playwright/test';

async function authenticate(page: Page) {
  await page.goto('/');
  await page.waitForSelector('button[type="submit"]');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/home');
}

export const test = base.extend({
  page: async ({ page }, use) => {
    await authenticate(page);
    await use(page);
  },
});

export { expect } from '@playwright/test';
```

Todos os spec files importam `test` e `expect` do fixture, não de `@playwright/test`.

---

## 6. Boas práticas

### Evitar `waitForTimeout`

Usar `waitForSelector`, `waitForFunction` ou assertions com retry ao invés de `waitForTimeout(N)`:

```typescript
// ❌ Ruim — timing-dependent, flaky em CI
await page.waitForTimeout(500);

// ✅ Bom — espera pela condição real
await expect(page.getByTestId('item-card')).toBeVisible({ timeout: 10000 });
```

### Padrão AAA (Arrange-Act-Assert)

```typescript
test('deve executar ação no item', async ({ page }) => {
  // Arrange
  const detailsPage = new ItemDetailsPage(page);
  await detailsPage.navigate('id-conhecido');

  // Act
  await detailsPage.actionsTab.executeAction('action-id', 'Justificativa');

  // Assert
  await expect(detailsPage.actionsTab.getActionStatus('action-id')).toHaveText('done');
});
```

### Isolar testes de helpers de QA

Helpers de QA (componentes que listam dados de exemplo na UI para facilitar testes manuais) podem causar `strict mode violation` por duplicar texto na página. Usar `data-testid` nos seletores evita este problema completamente.

### Validação visual com Playwright MCP

Para ajustes de CSS/layout, usar o Playwright MCP para validação visual antes de commitar:

1. `browser_navigate` → navegar para a página
2. `browser_evaluate` → focar elementos, inspecionar computed styles
3. `browser_take_screenshot` → capturar o resultado visual
4. Iterar até correto, só então commitar

---

## 7. Configuração

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env['CI'],
  retries: process.env['CI'] ? 2 : 0,
  workers: process.env['CI'] ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: '<DEV_URL>',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: '<DEV_CMD>',
    url: '<DEV_URL>',
    reuseExistingServer: !process.env['CI'],
    timeout: 120000,
  },
});
```

---

## 8. Dados de teste

Cada feature deve documentar seus próprios dados de teste em um README dentro de `<APP_DIR>/e2e/<feature>/` ou no Page Object correspondente. Pontos a observar ao definir mocks:

- **Validações:** dados mock devem passar pelas validações implementadas no frontend (CPF/CNPJ com dígito verificador, email RFC 5322, etc.)
- **Cenários compartilhados:** quando um teste depende de um valor compartilhado entre múltiplas entidades (ex: telefone duplicado para testar paginação), documente isso explicitamente
- **Estados variados:** prever fixtures para os principais estados (Active, Inactive, Blocked, etc.)
- **IDs estáveis:** usar IDs determinísticos no mock server para que os testes possam navegar diretamente para entidades conhecidas
