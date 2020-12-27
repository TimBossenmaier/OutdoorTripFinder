import {TourRaw} from './tour-raw';
import {Tour} from './tour';

export class TourFactory {

  static fromRaw(t: TourRaw): Tour{
    const activityType = t.activity_type;
    return {
      ...t,
      activityType
    };
  }

  static empty(): Tour {
    return {
      name: '',
      description: '',
      activityType: '',
      source: '',
      save_path: '',
      multi_day: 'false',
      locations: ['']
    };
  }
}
