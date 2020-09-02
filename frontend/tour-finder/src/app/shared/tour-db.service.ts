import { Injectable } from '@angular/core';

import { Tour } from './tour';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TourDbService {
  private apiURL = 'http://localhost:5000';

  constructor(private http: HttpClient) {

  }

  getAllTours(): Observable<Tour[]> {
    return this.http.get<any[]>(`${this.apiURL}/get_tour_demo`);
  }

  getTourByID(id: string): Observable<Tour> {
    return this.http.get<any>(`${this.apiURL}/get_by_id?id=${id}`);
  }
}
