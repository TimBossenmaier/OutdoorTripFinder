import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TourDbService } from '../shared/tour-db.service';
import {Tour } from '../shared/tour';
import {Comment} from '../shared/comment';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Observable} from 'rxjs';

@Component({
  selector: 'tf-tour-details',
  templateUrl: './tour-details.component.html',
  styleUrls: ['./tour-details.component.css']
})
export class TourDetailsComponent implements OnInit {
tour$: Observable<Tour>;
comments: Comment[];
commentForm: FormGroup;
blob: Blob;
fileType = '.pdf';
hikes: number;
userHiked: boolean;

  constructor(
    private tdb: TourDbService,
    private route: ActivatedRoute,
    private fb: FormBuilder
  ) { }

  ngOnInit(): void {
    const params = this.route.snapshot.paramMap;
    this.tour$ = this.tdb.getTourByID(params.get('id').toString());
    this.tdb.getCommentByAct(params.get('id').toString()).subscribe(c => this.comments = c);
    this.tdb.getHikes(params.get('id').toString()).subscribe(h => this.hikes = h);
    this.tdb.hike(params.get('id').toString(), 'check').subscribe(h => this.userHiked = h);
    $('#hikeButton')
      .popup()
    ;
    $('#remHikeButton')
      .popup()
    ;
    this.initForm();
  }

  private initForm() {
    if (this.commentForm) {return; }

    this.commentForm = this.fb.group(
      {
        body: ['', Validators.required]
      }
    );
  }

  download() {
    const params = this.route.snapshot.paramMap;
    this.tdb.getPDF(params.get('id').toString())
      .subscribe((data) => {this.blob = new Blob([data], {type: 'application/pdf'});

                            const downloadURL = window.URL.createObjectURL(data);
                            const link = document.createElement('a');
                            link.href = downloadURL;
                            link.download = $('#tourName').text().trim().concat(this.fileType);
                            link.click();
      });
  }

  addHike(): void {
    const params = this.route.snapshot.paramMap;
    this.tdb.hike(params.get('id').toString(), 'add').subscribe();
    this.tdb.getHikes(params.get('id').toString()).subscribe(h => this.hikes = h);
    this.tdb.hike(params.get('id').toString(), 'check').subscribe(h => this.userHiked = h);
    this.ngOnInit();
  }

  removeHike(): void {
    const params = this.route.snapshot.paramMap;
    this.tdb.hike(params.get('id').toString(), 'rem').subscribe();
    this.ngOnInit();
  }

  submitForm() {
    const formValue = this.commentForm.value;
    const activityID = this.route.snapshot.paramMap.get('id').toString();

    const comment: Comment = {
      ...formValue,
      activityID
    };
    this.tdb.createComment(comment).subscribe();
    this.tdb.getCommentByAct(activityID).subscribe(c => this.comments = c);
    this.commentForm.reset();
    this.ngOnInit();
  }

}
