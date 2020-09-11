import { Tour } from './tour';
import { TourRaw } from './tour-raw';

export class TourFactory {

  static fromRaw(t: TourRaw): Tour{
    return {
      ...t,
      id: t.id.toString()
    };
  }
}
