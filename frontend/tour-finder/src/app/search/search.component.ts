import { Component, OnInit } from '@angular/core';
import {Subject} from 'rxjs';
import {debounceTime, distinctUntilChanged, filter, switchMap, tap} from 'rxjs/operators';
import {TourDbService} from '../shared/tour-db.service';
import {Tour} from '../shared/tour';

@Component({
  selector: 'tf-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

  keyUp$ = new Subject<string>();
  isLoading = false;
  foundTours: Tour[] = [];

  constructor(private tdb: TourDbService) { }

  ngOnInit(): void {
    this.keyUp$.pipe(
      filter(term => term.length >= 3),
      debounceTime(500),
      distinctUntilChanged(),
      tap(() => this.isLoading = true),
      switchMap(searchTerm => this.tdb.getTourByTerm(searchTerm)),
      tap(() => this.isLoading = false)
    )
      .subscribe(tours => this.foundTours = tours);
  }

}
