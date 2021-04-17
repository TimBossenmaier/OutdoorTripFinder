import { TestBed } from '@angular/core/testing';

import { TourDbService } from './tour-db.service';

describe('TourDbService', () => {
  let service: TourDbService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TourDbService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
