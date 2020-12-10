import { Injectable } from '@angular/core';
import { catchError, map, retry } from 'rxjs/operators';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

import { Tour } from './tour';
import { TourRaw } from './tour-raw';
import { TourFactory } from './tour-factory';


@Injectable({
  providedIn: 'root'
})
export class TourDbService {
  private apiURL = 'http://192.168.0.174:5000';

  constructor(private http: HttpClient) {

  }

  getAllTours(): Observable<Tour[]> {
    return this.http.get<TourRaw[]>(`${this.apiURL}/get_tour_demo`)
      .pipe(
        retry(3),
        map( toursRaw => toursRaw.map(t => TourFactory.fromRaw(t))),
        catchError(this.errorHandler)
      );
  }

  getAllToursSearch(searchTerm: string): Observable<Tour[]> {
    return this.http.get<TourRaw[]>(`${this.apiURL}/search_tours?search=${searchTerm}`)
      .pipe(
        retry(3),
        map(toursRaw => toursRaw.map(t => TourFactory.fromRaw(t))),
        catchError(this.errorHandler)
      );
  }

  getTourByID(id: string): Observable<Tour> {
    return this.http.get<TourRaw>(`${this.apiURL}/main/activity/${id}`)
      .pipe(
        retry(3),
        map(t => TourFactory.fromRaw(t)),
        catchError(this.errorHandler)
    );
  }

  private errorHandler(error: HttpErrorResponse): Observable<any> {
    console.error('Fehler aufgetreten!');
    return throwError(error);
  }
}
