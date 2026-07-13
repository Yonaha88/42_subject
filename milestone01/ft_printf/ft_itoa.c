/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/07 13:27:04 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/07 13:29:30 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	count_digits(long nbr)
{
	int	digit;

	digit = 0;
	if (nbr < 0)
		digit++;
	if (nbr == 0)
		digit++;
	while (nbr)
	{
		nbr /= 10;
		digit++;
	}
	return (digit);
}

static void	fill_numptr(char *numptr, long nbr, int digit)
{
	int	idx;

	idx = digit;
	numptr[idx] = '\0';
	idx--;
	if (nbr < 0)
	{
		numptr[0] = '-';
		nbr = -nbr;
	}
	if (nbr == 0)
		numptr[idx] = '0';
	while (nbr > 0)
	{
		numptr[idx] = '0' + (nbr % 10);
		nbr /= 10;
		idx--;
	}
}

char	*ft_itoa(long nbr)
{
	char	*numptr;
	int		digit;

	digit = count_digits(nbr);
	numptr = (char *)malloc((digit + 1) * sizeof(char));
	if (numptr == NULL)
		return (NULL);
	fill_numptr(numptr, nbr, digit);
	return (numptr);
}
