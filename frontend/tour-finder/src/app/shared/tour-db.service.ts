import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

import { Tour } from './tour';
import { TourRaw } from './tour-raw';
import { TourFactory } from './tour-factory';


@Injectable({
  providedIn: 'root'
})
export class TourDbService {
  private apiURL = 'http://localhost:5000';

  constructor(private http: HttpClient) {

  }

  getAllTours(): Observable<Tour[]> {
    return this.http.get<TourRaw[]>(`${this.apiURL}/get_tour_demo`)
      .pipe(
        map( toursRaw => toursRaw.map(t => TourFactory.fromRaw(t)))
      );
  }

  getTourByID(id: string): Observable<Tour> {
    return this.http.get<TourRaw>(`${this.apiURL}/get_by_id?id=${id}`)
      .pipe(
      map(t => TourFactory.fromRaw(t))
    );
  }
}
