import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GoogleLocationSearchComponent } from './google-location-search.component';

describe('TestGoogleComponent', () => {
  let component: GoogleLocationSearchComponent;
  let fixture: ComponentFixture<GoogleLocationSearchComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GoogleLocationSearchComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GoogleLocationSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
