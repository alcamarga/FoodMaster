import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { AppComponent } from './app';
import { ApiHealthService } from './services/api-health.service';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        {
          provide: ApiHealthService,
          useValue: {
            obtenerSalud: () =>
              of({ status: 'ok', service: 'FoodMaster API' }),
          },
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render FoodMaster title', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('FoodMaster');
  });
});
