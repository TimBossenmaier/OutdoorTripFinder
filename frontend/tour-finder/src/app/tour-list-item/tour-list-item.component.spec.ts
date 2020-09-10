import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TourListItemComponent } from './tour-list-item.component';

describe('TourListItemComponent', () => {
  let component: TourListItemComponent;
  let fixture: ComponentFixture<TourListItemComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TourListItemComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TourListItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
